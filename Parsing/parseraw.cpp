//////////////////////////////////////////////////////////////////////////////////////////////////////////
//
//ParseRaw.exe
//
//This program parses .GPS log files containing ISMRAWOBSB, ISMDETOBSB, and/or ISMRAWTECB and outputs
//each log into an ASCII-formatted (CSV) file suitable for human viewing.  Legacy log formats RAWSINB and 
//DETRSINB are also supported.
//
//NOTE that these outputs are not equivalent to the "ASCII" versions of the same logs.
//
//Source:   NovAtel Inc.
//Date:     December 1, 2011
//
/////////////////////////////////////////////////////////////////////////////////////////////////////////
//
//FREEWARE USE LICENSE -
//NovAtel Inc. grants you, the end user, a nonexclusive, nontransferable license to 
//copy, modify and/or use the Freeware only for your internal purposes. You may not 
//copy, modify and/or use the Freeware for others. COPYING OR REPRODUCTION OF THE 
//FREEWARE TO ANY OTHER SERVER OR LOCATION FOR FURTHER REPRODUCTION OR REDISTRIBUTION 
//IS EXPRESSLY PROHIBITED, UNLESS SUCH REPRODUCTION OR REDISTRIBUTION IS EXPRESSLY 
//PERMITTED BY AN END USER LICENSE AGREEMENT PROVIDED SEPARATELY BY NOVATEL INC.
//
//NO SUPPORT PROVIDED -
//NovAtel Inc. endeavors to include useful Freeware on this Site. However, no support
//is provided for the Freeware and you use it at your own risk. 
//
//WARRANTY DISCLAIMER AND LIMITATION ON LIABILITY -
//NOVATEL INC. PROVIDES THE SOFTWARE "AS IS" AND WITHOUT WARRANTY OF ANY KIND, EXPRESS
//OR IMPLIED, INCLUDING WITHOUT LIMITATION ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
//FITNESS FOR A PARTICULAR PURPOSE.  NO ORAL OR WRITTEN INFORMATION OR ADVICE GIVEN TO
//YOU BY ANY EMPLOYEE, REPRESENTATIVE OR DISTRIBUTOR WILL CREATE A WARRANTY FOR THE SOFTWARE.
//
//IN NO EVENT SHALL NOVATEL INC. BE LIABLE FOR ANY SPECIAL, CONSEQUENTIAL, INCIDENTAL OR
//INDIRECT DAMAGES OF ANY KIND OR NATURE DUE TO ANY CAUSE.
//
/////////////////////////////////////////////////////////////////////////////////////////////////////////

//NovAtel builds of this software use proprietary code for recording and reporting the source code version.
//This is disabled in freeware versions of the source code through the use of the preprocessor directive 
//below.  Ensure that this value is always 0 for your own software builds.
#define ATNOVATEL 0

#if ATNOVATEL
   #include "NovAtel_Parse.h"
#endif

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <memory.h>
#include <math.h>

#define MAX_SYSTEMS 8 //GPS, GLONASS, GALILEO, WAAS, COMPASS, QZSS, 2 Unspecified
#define MAX_NUM_PRNS  32 //Per system
#define NO_START_TIME -1.0
#define NO_END_TIME   999999.0

#define POWER_D            2048.00
#define MAX_BUFFER_SIZE    204800  //Read 200 kB at a time from log file
#define MAX_LOG_SIZE       20000    //Max "raw" log size to be handled -- including buffer for future constellations
#define MAX_OUTFILE_NAME   250
#define VALID_OUTFILE_NAME 249
#define CRC32_POLYNOMIAL   0xEDB88320L //See NovAtel OEM6 firmware reference manual

#define BASE_PRN_SBAS      120
#define BASE_PRN_QZSS      183

bool    bRawSin,bDetrSin,bIsmRawObs,bIsmDetObs,bIsmRawTEC;
int     aiPrnStatsDetrended[MAX_SYSTEMS][MAX_NUM_PRNS];
int     aiPrnStatsRaw[MAX_SYSTEMS][MAX_NUM_PRNS];

#pragma pack(1)

typedef enum SYSTEM_TYPE
{
   SYS_GPS     = 0,
   SYS_GLO     = 1,
   SYS_SBAS    = 2,
   SYS_GAL     = 5,
   SYS_COMPASS = 6,
   SYS_QZSS    = 7,
   SYS_LBAND   = 8,
   SYS_UNKNOWN = 30,
   SYS_NONE    = 31
};

//RAWSINB/DETRSINB ADR & Power data format
typedef struct
{
   long   lAdr;
   long   lPower;
} SINB_DATA;

//RAWSINB/DETRSINB fields
typedef struct
{
   unsigned short usPrn;
   unsigned short usReserved;
   float          fTEC;
   float          fTECRate;
   double         dFirstADR;
   SINB_DATA      stSinb[50];
} SINB_CHANNEL_DATA;

//ISMRAWOBS/ISMDETOBS ADR & Power data format (bit field)
typedef struct
{
   signed long int     lDeltaAdr : 20;
   unsigned long int   lDeltaPower : 11;
   unsigned            sign : 1;
} RAWOBS_DATA;

//ISMRAWOBS/ISMDETOBS fields
typedef struct
{
   unsigned char     ucPrn;
   signed char       cFreq;
   unsigned char     ucSigType;
   unsigned char     ucReserved;
   double            dFirstADR;
   unsigned int      uiFirstPower;
   RAWOBS_DATA       stSinb[49];
} RAWOBS_CHANNEL_DATA; 

//ISMRAWTEC fields
typedef struct 
{
   unsigned char ucPrn;
   signed char   cFreq;
   unsigned char ucSvSys;
   unsigned char ucPrimSignal;
   unsigned char ucSecSignal;
   unsigned char ucReserved1;
   unsigned char ucReserved2;
   unsigned char ucReserved3;
   float         fTEC;
   float         fTECRate;    
} RAWTECB_DATA; 

//Standard NovAtel binary log header data
typedef struct
{
   unsigned char  ucSOP1;
   unsigned char  ucSOP2;
   unsigned char  ucSOP3;
   unsigned char  ucHeaderLength;
   unsigned short usMessageID;
   unsigned char  ucMessageType;
   unsigned char  ucPortAddress;
   unsigned short usMessageLength;
   unsigned short usSequence;
   unsigned char  ucIdleTime;
   unsigned char  ucTimeStatus;
   unsigned short usWeek;
   unsigned long  ulMilliSecs;
   unsigned long  ulRxStatus;
   unsigned short usReserved;
   unsigned short usSWVersion;
} HEADER_DATA;

void
Usage( void)
{
   fprintf(stderr, "Usage: ParseRaw <PRN> <IF>  [OF] [ST] [ET] [SW] [EW]\r\n");
   fprintf(stderr, "                PRN = G<X> to output specific GPS PRN X\r\n");
   fprintf(stderr, "                    = R<X> to output specific GLO Slot X\r\n");
   fprintf(stderr, "                    = S<X> to output specific SBAS PRN X\r\n");
   fprintf(stderr, "                    = E<X> to output specific GAL PRN X\r\n");
   fprintf(stderr, "                    = C<X> to output specific COMPASS PRN X\r\n");
   fprintf(stderr, "                    = Q<X> to output specific QZSS PRN X\r\n");
   fprintf(stderr, "                PRN = 0 will just output log stats\r\n");
   fprintf(stderr, "                IF  = input path and filename\r\n");
   fprintf(stderr, "                OF  = output path and filename (optional if PRN = 0)\r\n");
   fprintf(stderr, "                ST  = start time (optional)\r\n");
   fprintf(stderr, "                ET  = end time (optional)\r\n");
   fprintf(stderr, "                SW  = start week (GPS week #) -- Required if ST specified and\r\n");
   fprintf(stderr, "                                                 data contains a week rollover\r\n");
   fprintf(stderr, "                EW  = end time (GPS week #) -- Required if ET specified and\r\n");
   fprintf(stderr, "                                               data contains a week rollover\r\n");
   fprintf(stderr, "                \r\n");
   exit(1);
}

unsigned long
CRC32Value( int iIndex_ )
{
   int j;
   unsigned long ulCRC;

   ulCRC = iIndex_;

   for( j = 8; j > 0; j-- )
   {
      if( ulCRC & 1 )
         ulCRC = (ulCRC >> 1) ^ CRC32_POLYNOMIAL;
      else
        ulCRC >>= 1;
   }

   return ulCRC;
}

bool
CheckCrcOk( unsigned char* pucStr_, int iLength_ )
{
   //The algorithm for computing NovAtel log CRCs is described in NovAtel's 
   //OEM6 Firmware Reference Manual.  This function is based on that algorithm.
   unsigned long ulTemp1;
   unsigned long ulTemp2;
   unsigned long ulCRC = 0;
   unsigned long ulStoredCRC;
   unsigned long ulCount;

   //Back up 4 bytes (length of CRC) and read in the value in the log
   ulCount = iLength_ - 4;
   ulStoredCRC = *((unsigned long*)&pucStr_[ulCount]);

   while( ulCount-- != 0 )
   {
      ulTemp1 = (ulCRC >> 8) & 0x00FFFFFFL;
      ulTemp2 = CRC32Value( ((int) ulCRC ^ *pucStr_++ ) & 0xFF ); 
      ulCRC = ulTemp1 ^ ulTemp2;
   }

   if( ulCRC == ulStoredCRC )
   {
      return true;
   }
   else
   {
      return false;
   }
}

void
ParseLog_RAWSIN( unsigned char* pucStr_, unsigned long ulRequestedPrn_, SYSTEM_TYPE eSystemChoice_, FILE* fOut_, bool bDetrended_ )
{
   unsigned long  ulTowMilliSecs;
   unsigned long  ulNumObservations;
   double         dADR;
   double         dPower;
   static bool    bRaw_FirstRawSin = true;
   static bool    bDET_FirstRawSin = true;
   
   SINB_CHANNEL_DATA stSinbChanData;
   HEADER_DATA  stSinbHeaderData;

   stSinbHeaderData = *((HEADER_DATA*) &pucStr_[0]);
   ulTowMilliSecs = stSinbHeaderData.ulMilliSecs;
   ulNumObservations = pucStr_[sizeof(HEADER_DATA)];
   
   for( int i = 0; i < (int) ulNumObservations ; i++ )
   {
      stSinbChanData  = *((SINB_CHANNEL_DATA*) &pucStr_[stSinbHeaderData.ucHeaderLength+4 + i*sizeof(SINB_CHANNEL_DATA)]);

      if( bDetrended_ )
      {
         aiPrnStatsDetrended[SYS_GPS][stSinbChanData.usPrn-1]++;
      }
      else
      {
         aiPrnStatsRaw[SYS_GPS][stSinbChanData.usPrn-1]++;
      }

      if( (unsigned long) stSinbChanData.usPrn == ulRequestedPrn_ 
           && eSystemChoice_ == SYS_GPS)
      {
         if( fOut_!=NULL)
         { 
            if( bDetrended_ &&  bDET_FirstRawSin)
            {
               fprintf( fOut_, "GPS TOW,TEC,TECdot,ADR,Power\n" );
               bDetrSin=true;
               bDET_FirstRawSin = false;
            }
            else if (!bDetrended_ && bRaw_FirstRawSin)
            {
               fprintf( fOut_, "GPS TOW,TEC,TECdot,ADR,Power\n" );
               bRawSin=true;
               bRaw_FirstRawSin = false;
            }

            for( int j = 0; j < 50; j++ )
            {
               dADR = stSinbChanData.stSinb[j].lAdr/1000.0;

               if( bDetrended_ )
                  dPower = stSinbChanData.stSinb[j].lPower/1048576.0;
               else
                  dPower = stSinbChanData.stSinb[j].lPower*10000.0;
                    
               fprintf( fOut_, "%10.3f,%9.6f,%9.6f,%12.3lf,%11.8lf\n", (double) ulTowMilliSecs/1000.0, stSinbChanData.fTEC,
                        stSinbChanData.fTECRate, stSinbChanData.dFirstADR+dADR, dPower );
               
               ulTowMilliSecs += 20;
            }
            continue; //continue to compute the total logs for each available PRN correctly
         }
      }
   }
}

void 
ParseLog_OBS( unsigned char* pucStr_, unsigned long ulRequestedPrn_, SYSTEM_TYPE eSystemChoice_, FILE* fOut_, bool bDetrended_ )
{
   unsigned long        ulTowMilliSecs;
   unsigned long        ulObservations;
   static bool          bRAW_FirstRawObs = true;
   static bool          bDET_FirstRawObs = true; 
   RAWOBS_CHANNEL_DATA  stSinbChanData;
   HEADER_DATA          stSinbHeaderData;
   static int           SvIdentifier = -999;
   double               adr_sum;
   double               dPower;
   int                  iTempPRN;
   char                 cGNSS[20]; //Name of current GNSS system for log output
   char                 cGNSS_SigType[2000]; //Name of current GNSS system for log output

   stSinbHeaderData = *((HEADER_DATA*) &pucStr_[0]);
   ulObservations = pucStr_[sizeof(HEADER_DATA)+4];

   for( int i = 0; i < (int) ulObservations ; i++ )
   {   
      stSinbChanData  = *((RAWOBS_CHANNEL_DATA*) &pucStr_[stSinbHeaderData.ucHeaderLength+8 + i*sizeof(RAWOBS_CHANNEL_DATA)]);
      ulTowMilliSecs = stSinbHeaderData.ulMilliSecs;

      if(pucStr_[sizeof(HEADER_DATA)] == SYS_QZSS)
         iTempPRN = stSinbChanData.ucPrn - BASE_PRN_QZSS +1;
      else if(pucStr_[sizeof(HEADER_DATA)] == SYS_SBAS)
         iTempPRN = stSinbChanData.ucPrn - BASE_PRN_SBAS +1;
      else
         iTempPRN = stSinbChanData.ucPrn;

      if( bDetrended_ )
         aiPrnStatsDetrended[pucStr_[sizeof(HEADER_DATA)]][(int)iTempPRN-1]++;
      else
         aiPrnStatsRaw[pucStr_[sizeof(HEADER_DATA)]][(int)iTempPRN-1]++;

      if( (unsigned long) stSinbChanData.ucPrn == ulRequestedPrn_ &&
           pucStr_[sizeof(HEADER_DATA)] == eSystemChoice_)
      {
         if( fOut_ != NULL )
         {
            switch ((int)  eSystemChoice_)
            {
          	case  SYS_GPS: 
                strcpy_s(cGNSS_SigType,"GPS Signal Type: 1 = L1CA, 4 = L2Y,  5 = L2C, 6 = L2P,    7 = L5Q");
				strcpy_s(cGNSS,"GPS");
                break;
            case  SYS_GLO: 
                strcpy_s(cGNSS,"GLONASS");
				strcpy_s(cGNSS_SigType,"GLONASS Signal Type: 1 = L1CA, 3 = L2CA, 4 = L2P\n\nFrequency: GLONASS frequency channel (-7 to +6)");
                break;
            case  SYS_SBAS: 
                strcpy_s(cGNSS,"SBAS");
				strcpy_s(cGNSS_SigType,"SBAS Signal Type: 1 = L1CA, 2 = L5I");
                break;
            case  SYS_GAL: 
                strcpy_s(cGNSS,"Galileo");
				strcpy_s(cGNSS_SigType,"Galileo Signal Type: 1 = E1,   2 = E5A,  3 = E5B, 4 = ALTBOC, 5 = E6");
                break;
            case  SYS_COMPASS: 
                strcpy_s(cGNSS,"COMPASS");
				strcpy_s(cGNSS_SigType,"COMPASS Signal Type: 1 = E2");
                break;
            case  SYS_QZSS: 
                strcpy_s(cGNSS,"QZSS");
				strcpy_s(cGNSS_SigType,"QZSS Signal Type: 1 = L1CA, 3 = L2C,  4 = L5Q");
                break;
            case  SYS_LBAND: 
                strcpy_s(cGNSS,"LBAND");
				strcpy_s(cGNSS_SigType," ");
                break;
            }
             
            if( bDET_FirstRawObs && bDetrended_)
            {
               //First log; print the header for detrended data
               bDET_FirstRawObs=false;
               fprintf(fOut_, "GPS TOW,Freq,SigType,ADR,Power\n" );
               bIsmDetObs = true;
            }
            else if(bRAW_FirstRawObs && !bDetrended_)
            {
               //First log; print the header for raw data
               bRAW_FirstRawObs=false;
               fprintf(fOut_, "GPS TOW,Freq,SigType,ADR,Power\n" );
               bIsmRawObs = true;
            }
                   
            if ( SvIdentifier !=  pucStr_[sizeof(HEADER_DATA)] ) //avoid repeating SvIdentifier tag
            {
               SvIdentifier =   pucStr_[sizeof(HEADER_DATA)];
            }
            
            if( bDetrended_ )
                  dPower = (double) stSinbChanData.uiFirstPower/1048576.0;
            else
                  dPower = (double) stSinbChanData.uiFirstPower*10000.0;
            
            fprintf( fOut_, "%10.3f, %d,%d,%6.8lf,%11.8lf\n", (double) ulTowMilliSecs/1000.0, stSinbChanData.cFreq,
                     stSinbChanData.ucSigType , stSinbChanData.dFirstADR, dPower);
               
            adr_sum=stSinbChanData.dFirstADR;

            for( int j = 0; j < 49; j++ )
            {
               
               ulTowMilliSecs += 20;
               if( NULL != fOut_ )
               {
                  if( stSinbChanData.stSinb[j].sign == 0 )
                     dPower=stSinbChanData.uiFirstPower * (POWER_D/(stSinbChanData.stSinb[j].lDeltaPower+1.0));
                  else
                     dPower=stSinbChanData.uiFirstPower * (stSinbChanData.stSinb[j].lDeltaPower+1.0)/POWER_D;
                  
                  if( bDetrended_ )
                     dPower = dPower/1048576.0;
                  else
                     dPower = dPower*10000.0;
                                    
                  adr_sum=stSinbChanData.stSinb[j].lDeltaAdr/1000.0 + adr_sum;
                  fprintf( fOut_, "%10.3f, %d,%d,%6.8lf,%11.8lf\n", (double) ulTowMilliSecs/1000.0, stSinbChanData.cFreq,
                           stSinbChanData.ucSigType, adr_sum, dPower );
               }
            }
         }
      }
   }
}

void
ParseLog_TEC( unsigned char* pucStr_, unsigned long ulRequestedPrn_, SYSTEM_TYPE eSystemChoice_, FILE* fOutTEC_, bool bDetrended_ )
{
   unsigned long  ulTowMilliSecs;
   unsigned long  ulObservations;
   static bool    bFirst = true;
   RAWTECB_DATA   stRawTECChanData_n;
   HEADER_DATA    stSinbHeaderData;
   char           cGNSS[20]; //Name of current GNSS system for log output

   stSinbHeaderData = *((HEADER_DATA*) &pucStr_[0]);
   ulObservations = pucStr_[sizeof(HEADER_DATA)];
   
   for( int i = 0; i <(int) ulObservations ; i++ )
   {
      stRawTECChanData_n  = *((RAWTECB_DATA*) &pucStr_[stSinbHeaderData.ucHeaderLength+4 + i*sizeof(RAWTECB_DATA)]);
      ulTowMilliSecs = stSinbHeaderData.ulMilliSecs;
      if( (unsigned long) stRawTECChanData_n.ucPrn == ulRequestedPrn_ &&
           stRawTECChanData_n.ucSvSys == eSystemChoice_)
      {
         if( NULL!= fOutTEC_ )
         {
            switch ((int)  eSystemChoice_)
            {
            case  SYS_GPS: 
               strcpy_s(cGNSS,"GPS");
               break;
            case  SYS_GLO: 
               strcpy_s(cGNSS,"GLONASS");
               break;
            case  SYS_SBAS: 
               strcpy_s(cGNSS,"SBAS");
               break;
            case  SYS_GAL: 
               strcpy_s(cGNSS,"Galileo");
               break;
            case  SYS_COMPASS: 
               strcpy_s(cGNSS,"COMPASS");
               break;
            case  SYS_QZSS: 
               strcpy_s(cGNSS,"QZSS");
               break;
            case  SYS_LBAND: 
               strcpy_s(cGNSS,"LBAND");
               break;
            }
            if( bFirst )
            {
               fprintf ( fOutTEC_, "GPS TOW,Freq,SV Sys,PrimSig,SigType,TEC,TECdot\n" );
               bFirst     = false;
               bIsmRawTEC = true; //flag raw log exists
            }
            
            fprintf(fOutTEC_,"%10.3f,%d,%d,%d,%d,%9.6f,%9.6f\n",(double) ulTowMilliSecs/1000.0,stRawTECChanData_n.cFreq,
            stRawTECChanData_n.ucSvSys,stRawTECChanData_n.ucPrimSignal,stRawTECChanData_n.ucSecSignal,stRawTECChanData_n.fTEC,stRawTECChanData_n.fTECRate);
         }
      }
   }
}

void
ScanForLogs( FILE* fIn_, 
             unsigned long ulPrn_, 
             SYSTEM_TYPE eSystemChoice_, 
             FILE* fOut_RAWSIN, 
             FILE* fOut_DETRSIN, 
             FILE* fOut_ISMRAWOBS, 
             FILE* fOut_ISMDETOBS, 
             FILE* fOut_ISMRAWTEC, 
             double dStartTime_, 
             double dEndTime_,
             unsigned short usStartWeek_,
             unsigned short usEndWeek_)
{
   int            i, j;
   bool           bDetrended;
   unsigned char  aucParseString[MAX_LOG_SIZE];
   unsigned char  aucFileBuffer[MAX_BUFFER_SIZE];
   unsigned char  aucTempFileBuffer[MAX_BUFFER_SIZE];
   unsigned char  ucHeaderLength;
   unsigned long  ulMessageID;
   unsigned long  ulMessageLength;
   int            iBufferPtr = NULL;
   int            iBytesRead = 0;
   int            iBufferSize = 0;
   bool           bFileExhausted = false;

   for( i = 0; i < MAX_SYSTEMS; i++ )
   {
      for( j = 0; j < MAX_NUM_PRNS; j++ )
      {
         aiPrnStatsDetrended[i][j] = 0;
         aiPrnStatsRaw[i][j] = 0;
      }
   }

   //Load buffer for the first time
   iBytesRead = fread( aucFileBuffer, 1, MAX_BUFFER_SIZE, fIn_ );
   iBufferPtr = 0;
   if(iBytesRead < MAX_BUFFER_SIZE)
      bFileExhausted = true;

   iBufferSize = iBytesRead;

   while( 1 )
   {
      if(iBufferPtr >= iBufferSize)
         break;

      aucParseString[0] = aucFileBuffer[iBufferPtr++];

      if( aucParseString[0] == 0xAA )
      {
         aucParseString[1] = aucFileBuffer[iBufferPtr++];
         if( aucParseString[1] == 0x44 )
         {
            aucParseString[2] = aucFileBuffer[iBufferPtr++];
            if( aucParseString[2] == 0x12 )
            {
               aucParseString[3] = aucFileBuffer[iBufferPtr++];
               ucHeaderLength = aucParseString[3];
               aucParseString[4] = aucFileBuffer[iBufferPtr++];
               aucParseString[5] = aucFileBuffer[iBufferPtr++];
               ulMessageID = (unsigned long)aucParseString[4] | ((unsigned long)aucParseString[5] << 8);
               // ------------Message ID----------------
               // Legacy: RAWSINB 327 (0x147), DETRSINB 326 (0x146)
               // New   : ISMRAWOBSB 1389 (0x56D), ISMRAWTECB 1390 (0x56E), ISMDETOBS 1395 (0x573), 
               aucParseString[6] = aucFileBuffer[iBufferPtr++];// Message Type
               aucParseString[7] = aucFileBuffer[iBufferPtr++];// Port Address
               aucParseString[8] = aucFileBuffer[iBufferPtr++];
               aucParseString[9] = aucFileBuffer[iBufferPtr++];

               ulMessageLength = (unsigned long)aucParseString[8] | ((unsigned long)aucParseString[9] << 8);

               if( (ulMessageID == 0x146 || 
                    ulMessageID == 0x147 || 
                    ulMessageID == 0x56D || 
                    ulMessageID == 0x56E || 
                    ulMessageID == 0x573) && 
                    ulMessageLength < MAX_LOG_SIZE)
               {
                  if ( ulMessageID == 0x147 || ulMessageID == 0x56D || ulMessageID == 0x56E )
                     bDetrended=false;
                  else
                     bDetrended=true;

                  for( int i = 0; i < (ulMessageLength + ucHeaderLength - 6); i++ )
                  {
                     aucParseString[i+10] = aucFileBuffer[iBufferPtr++];
                  }
                  
                  if( CheckCrcOk( &aucParseString[0], ulMessageLength + ucHeaderLength + 4 ) )
                  {
                     unsigned long ulTowMilliSecs;
                     unsigned short usWeek;

                     usWeek = *((unsigned short*) &aucParseString[14]);
                     ulTowMilliSecs = *((unsigned long*) &aucParseString[16]);
                     
                     if( dStartTime_ == NO_START_TIME )
                     {
                        dStartTime_ = (double) ulTowMilliSecs/1000.0;
                     }
                     if( usStartWeek_ == 0 )
                     {
                        usStartWeek_ = usWeek;
                     }

                     if( dEndTime_ != NO_END_TIME )
                     {
                        if( usEndWeek_ != 0  &&
                            (ulTowMilliSecs/1000.0) > dEndTime_  &&
                            usWeek >= usEndWeek_)
                        {
                           //End time and week have been passed
                           break;
                        }
                        else if( usEndWeek_ == 0 && 
                                 (ulTowMilliSecs/1000.0) > dEndTime_ )
                        {
                           //End time (assume this week) has been passed
                           break;
                        }
                     }

                     if( ((ulTowMilliSecs / 1000.0) >= dStartTime_ && usWeek == usStartWeek_ ) ||
                           usWeek > usStartWeek_)
                     {
                        //We've passed the start time (but not the end time); parse this log
                        if      ( ulMessageID == 0x147) ParseLog_RAWSIN( &aucParseString[0], ulPrn_, eSystemChoice_, fOut_RAWSIN, bDetrended );   //for rawsin and TEC (single file)
                        else if ( ulMessageID == 0x146) ParseLog_RAWSIN( &aucParseString[0], ulPrn_, eSystemChoice_, fOut_DETRSIN, bDetrended );  //for detrended sin
                        else if ( ulMessageID == 0x56D) ParseLog_OBS( &aucParseString[0], ulPrn_, eSystemChoice_, fOut_ISMRAWOBS, bDetrended );   //for raw obs
                        else if ( ulMessageID == 0x573) ParseLog_OBS( &aucParseString[0], ulPrn_, eSystemChoice_, fOut_ISMDETOBS, bDetrended );   //for detrended obs logs
                        else if ( ulMessageID == 0x56E) ParseLog_TEC( &aucParseString[0], ulPrn_, eSystemChoice_, fOut_ISMRAWTEC, bDetrended );   //for raw TEC logs
                     }
                  }
               }
               else
               {
                  //Skip current message (including CRC) -- 
                  //message length + header length - 10 bytes into current message + 4 byte CRC
                  iBufferPtr += (ulMessageLength + ucHeaderLength - 6);
               }
            }
            else
            {
               //Preamble failure. Back up to check the next byte
               iBufferPtr -= 2;
            }
         }
         else
         {
            //Preamble failure. Back up to check the next byte
            iBufferPtr -= 1;
         }
      }
      
      if(iBufferPtr >= (MAX_BUFFER_SIZE - MAX_LOG_SIZE) && !bFileExhausted)
      {
         //Shift everything left in the buffer to the start, then read in the correct number of 
         //bytes to fill up the rest of the buffer.
         int i;
         int iNumUsed = iBufferPtr;                   //Number of bytes we've used from the buffer in previous parsing
         int iNumLeft = MAX_BUFFER_SIZE - iBufferPtr; //Number of un-parsed bytes remaining in the buffer
         for(i = 0; i < iNumLeft; i++)
         {
            aucTempFileBuffer[i] = aucFileBuffer[iBufferPtr++];
         }
         
         //Read in bytes to replace those used in previous parsing
         iBytesRead = fread( &(aucTempFileBuffer[i]), 1, iNumUsed, fIn_ );
         if(iBytesRead != iNumUsed)
         {
            //No more bytes left after this buffer is finished
            bFileExhausted = true;
            
         }
         //Buffer now has leftover bytes + new bytes read in
         iBufferSize = iNumLeft + iBytesRead;
         
         iBufferPtr = 0;

         for(i = 0; i < MAX_BUFFER_SIZE; i++)
            aucFileBuffer[i] = aucTempFileBuffer[i];
      }
   }

   fprintf( stdout, "\nPrn #Detrended       #Raw\n" );
   for( i = 0; i < MAX_SYSTEMS; i++ )
   {
      switch(i)
      {
      case SYS_GPS:
         fprintf(stdout, "\nSystem GPS\n");
         break;
      case SYS_GLO:
         fprintf(stdout, "\nSystem GLONASS\n");
         break;
      case SYS_GAL:
         fprintf(stdout, "\nSystem GALILEO\n");
         break;
      case SYS_QZSS:
         fprintf(stdout, "\nSystem QZSS\n");
         break;
      case SYS_SBAS:
         fprintf(stdout, "\nSystem SBAS\n");
         break;
      case SYS_COMPASS:
         fprintf(stdout, "\nSystem COMPASS\n");
         break;
      }

      for( j = 0; j < MAX_NUM_PRNS; j++ )
      {
         if( aiPrnStatsDetrended[i][j] > 0 || aiPrnStatsRaw[i][j] > 0 )
         {
            fprintf(stdout, "%3d %10d %10d\n", (i == SYS_SBAS ? j+BASE_PRN_SBAS : (i == SYS_QZSS ? j+BASE_PRN_QZSS : j+1)), aiPrnStatsDetrended[i][j], aiPrnStatsRaw[i][j] );
         }
      }
   }
   fprintf(stdout, "\n");
}

int main( int argc, char* argv[] )
{
   char*          pcPRNSelector;
   SYSTEM_TYPE    eSystemChoice = SYS_NONE;
   unsigned long  ulPrn = 0;
   double         dStartTime;
   double         dEndTime;
   unsigned short usStartWeek = 0;
   unsigned short usEndWeek = 0;
   char*          szInFileName = NULL;
   char*          szOutFileName = NULL;
   char           szOut_RAWSIN_file[MAX_OUTFILE_NAME];
   char           szOut_DETRSIN_file[MAX_OUTFILE_NAME];
   char           szOut_ISMRAWOBS_file[MAX_OUTFILE_NAME];
   char           szOut_ISMDETOBS_file[MAX_OUTFILE_NAME];
   char           szOut_ISMRAWTEC_file[MAX_OUTFILE_NAME];
   FILE*          fIn;
   FILE*          fOut_RAWSIN = NULL;
   FILE*          fOut_DETRSIN = NULL;
   FILE*          fOut_ISMRAWOBS = NULL;
   FILE*          fOut_ISMDETOBS = NULL;
   FILE*          fOut_ISMRAWTEC = NULL;
   errno_t        err;
     
   printf("\nGPStation-6 Raw Observation Post-Processing Utility\n");
#if ATNOVATEL
   //More detailed version information based on NovAtel's VCS
   PrintVersion();
#endif

   if( argc != 3 && argc != 4 && argc != 6 && argc != 8 )
   {
      //Invalid command line
      Usage();
   }
   else
   {
      //PRN
      pcPRNSelector = argv[1];
      switch( pcPRNSelector[0] )
      {
      case 'G':
      case 'g':
         eSystemChoice = SYS_GPS;
         break;
      case 'R':
      case 'r':
         eSystemChoice = SYS_GLO;
         break;
      case 'E':
      case 'e':
         eSystemChoice = SYS_GAL;
         break;
      case 'C':
      case 'c':
         eSystemChoice = SYS_COMPASS;
         break;
      case 'S':
      case 's':
         eSystemChoice = SYS_SBAS;
         break;
      case 'Q':
      case 'q':
         eSystemChoice = SYS_QZSS;
         break;
      case '0':
         break;
      default:
         fprintf(stderr, "Invalid System chosen for selected PRN\r\n");
         Usage();
      }

      if(sizeof(pcPRNSelector) > 1)
         //User entered a system & value, presumably!
         ulPrn = atol( &pcPRNSelector[1] );
      
      //Input Filename
      szInFileName  = argv[2];

      //Output Filename
      if(argc >= 4)
      {
         szOutFileName = argv[3];
         if (szOutFileName != NULL)
         {
            if (strlen(szOutFileName) > VALID_OUTFILE_NAME)
            {
               fprintf(stderr, "Can't open output file: file name is too long %s\r\n", szOutFileName );
               Usage();
            }
         }
      }

      //Start and end times, if supplied
      if( argc == 6 || argc == 8)
      {
         dStartTime = atof(argv[4]);
         dEndTime   = atof(argv[5]);
      }
      else
      {
         dStartTime = NO_START_TIME;
         dEndTime   = NO_END_TIME;
      }

      if( argc == 8 )
      {
         usStartWeek = atoi(argv[6]);
         usEndWeek = atoi(argv[7]);
         if(usEndWeek < usStartWeek)
         {
            fprintf(stderr, "End week is earlier than start week\n", szOutFileName );
            Usage();
         }
      }
   }

   err = fopen_s(&fIn, szInFileName, "rb");
   if( err != 0 )
   {
      fprintf(stderr, "Can't open file: %s\r\n", szInFileName );
      Usage();
   }
 
   if( szOutFileName != NULL )
   {
      //Create and open individual output file for each log, since we don't know
      //what's contained in the log until we scan through it
      strcpy_s(szOut_RAWSIN_file, "RawSin_");
      strcpy_s(szOut_DETRSIN_file, "DetrSin_");
      strcpy_s(szOut_ISMRAWOBS_file, "IsmRawObs_");
      strcpy_s(szOut_ISMDETOBS_file, "IsmDetObs_");
      strcpy_s(szOut_ISMRAWTEC_file, "IsmRawTEC_");
      strcat_s(szOut_RAWSIN_file, szOutFileName);
      strcat_s(szOut_DETRSIN_file, szOutFileName);
      strcat_s(szOut_ISMRAWOBS_file, szOutFileName);
      strcat_s(szOut_ISMDETOBS_file, szOutFileName);
      strcat_s(szOut_ISMRAWTEC_file, szOutFileName);

      err= fopen_s(&fOut_RAWSIN, szOut_RAWSIN_file, "wb");
      err= fopen_s(&fOut_DETRSIN, szOut_DETRSIN_file, "wb");
      err= fopen_s(&fOut_ISMRAWOBS, szOut_ISMRAWOBS_file, "wb");
      err= fopen_s(&fOut_ISMDETOBS, szOut_ISMDETOBS_file, "wb");
      err= fopen_s(&fOut_ISMRAWTEC, szOut_ISMRAWTEC_file, "wb");
      
      if( err!=0)
      {
         fprintf(stderr, "Can't open file: %s\r\n", szOutFileName );
         Usage();
      } 
   }
   else
   {
      err= fopen_s(&fOut_RAWSIN, "RAWSIN_TEMP.tm0", "wb");
      err= fopen_s(&fOut_DETRSIN, "DETRSIN_TEMP.tm0", "wb");
      err= fopen_s(&fOut_ISMRAWOBS, "RAWOBS_TEMP.tm0", "wb");
      err= fopen_s(&fOut_ISMDETOBS, "DETOBS_TEMP.tm0", "wb");
      err= fopen_s(&fOut_ISMRAWTEC, "RAWTEC_TEMP.tm0", "wb");
   }
  
   //Scan input file and write logs as they're encountered
   ScanForLogs( fIn, 
                ulPrn, 
                eSystemChoice, 
                fOut_RAWSIN, 
                fOut_DETRSIN, 
                fOut_ISMRAWOBS, 
                fOut_ISMDETOBS, 
                fOut_ISMRAWTEC, 
                dStartTime, 
                dEndTime,
                usStartWeek,
                usEndWeek);

   _fcloseall() ;
   
   //don't like empty files so remove them
   if (!bRawSin) remove(szOut_RAWSIN_file);
   if (!bDetrSin) remove(szOut_DETRSIN_file);
   if (!bIsmRawObs) remove(szOut_ISMRAWOBS_file);
   if (!bIsmDetObs) remove(szOut_ISMDETOBS_file);
   if (!bIsmRawTEC) remove(szOut_ISMRAWTEC_file);
   
   return 0;
}