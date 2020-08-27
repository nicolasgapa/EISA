//////////////////////////////////////////////////////////////////////////////////////////////////////////
//
//Parsereduced.exe
//
//This program parses .GPS log files containing ISMREDOBSB, ISMREDTECB outputs. 
//Legacy log formats ISMRB is also supported.
//Outputs each log into an ASCII-formatted (CSV) file suitable for human viewing.
//
//NOTE that these outputs are NOT equivalent to the "ASCII" versions of the same logs
//as output from the NovAtel GPStation-6.
//
//Source:   NovAtel Inc.
//Date:     December 5, 2011
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
#include <io.h>
#include <stdlib.h>
#include <string.h>
#include <memory.h>


#define JUST_AZ_EL         0
#define MAX_NUM_PRNS       50
#define ALL_PRNS           1025
#define MAX_OUTFILE_NAME   250
#define VALID_OUTFILE_NAME 249
#define MAX_BUFFER_SIZE	   204800      //Read 200 kB at a time from log file
#define MAX_LOG_SIZE       20000       //Max "raw" log size to be handled -- including buffer for future constellations
#define CRC32_POLYNOMIAL   0xEDB88320L //See NovAtel OEM6 firmware reference manual

bool bIsmr,bRedObs,bRedTEC;

//For proper byte alignment within structs
#pragma pack(1)

//ISMR fields
typedef struct
{
   unsigned long  ulPrn;
   float          fAzimuth;
   float          fElevation;
   double         dCNo;
   double         dS4;
   double         dS4Correction;
   double         d1SecSigma;
   double         d3SecSigma;
   double         d10SecSigma;
   double         d30SecSigma;
   double         d60SecSigma;
   double         dCodeCarrier;
   double         dCodeCarrierStdDev;
   float          fTEC45;
   float          fTECRate45;
   float          fTEC30;
   float          fTECRate30;
   float          fTEC15;
   float          fTECRate15;
   float          fTEC0;
   float          fTECRate0;
   double         dLockTime;
   unsigned long  ulStatus;
   double         dL2LockTime;
   double         dL2CNo;
} ISMR_CHANNEL_DATA;

//ISM Reduced Observation fields
typedef struct
{
   unsigned char ucPrn;
   signed char   cFreq;
   unsigned char ucSvSys;
   unsigned char ucSigType;
   float         fAzimuth;
   float         fElevation;
   float         fCNo;
   float         fLockTime;
   float         fCMCAvrg;
   float         fCMCStd;
   float         fS4;
   float         fS4Correction;
   float         f1SecSigma;
   float         f3SecSigma;
   float         f10SecSigma;
   float         f30SecSigma;
   float         f60SecSigma;
} ISMREDOBS_CHANNEL_DATA;

//ISM Reduced TEC fields
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
   float         fAzimuth;
   float         fElevation;
   float         fSecSigLckTime;
   float         fSecSigCNo;
   float         fTEC15;
   float         fdTEC15;
   float         fTEC30;
   float         fdTEC30;
   float         fTEC45;
   float         fdTEC45;
   float         fTECTOW;
   float         fdTECTOW;
} ISMREDTEC_CHANNEL_DATA;

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

typedef enum SYSTEM_TYPE
{
   SYS_GPS     = 0,
   SYS_GLO     = 1,
   SYS_SBAS    = 2,
   SYS_GAL     = 5,
   SYS_COMPASS = 6,
   SYS_QZSS    = 7,
   SYS_LBAND   = 8,
   SYS_UNKNOWN = 14,
   SYS_NONE    = 15
};

////////////////////////////////////////////////
//void Usage()
//
//Output help message and quit program
//
////////////////////////////////////////////////
void
Usage()
{
   fprintf(stderr, "\nUsage: ParseReduced <PRN> <IF>  <OF>\r\n");
   fprintf(stderr, "                PRN = G<X> to output specific GPS PRN X\r\n");
   fprintf(stderr, "                    = R<X> to output specific GLO Slot X\r\n");
   fprintf(stderr, "                    = S<X> to output specific SBAS PRN X\r\n");
   fprintf(stderr, "                    = E<X> to output specific GAL PRN X\r\n");
   fprintf(stderr, "                    = C<X> to output specific COMPASS PRN X\r\n");
   fprintf(stderr, "                    = Q<X> to output specific QZSS PRN X\r\n");
   fprintf(stderr, "                      No PRN # output all PRN's for a specific SV system\r\n");
   fprintf(stderr, "                 X  = 0 to output only azimuth and elevation for a specific SV system\r\n");
   fprintf(stderr, "                 IF = Input path and filename \r\n");
   fprintf(stderr, "                 OF = output path and filename\r\n");

   _fcloseall();
   exit(1);
}

////////////////////////////////////////////////
//void ParseLog_ISMR( ... )
//
//Parse a single instance of the legacy ISMR log, if the chosen system is "GPS," and write
//the formatted data into the output CSV file designated for ISMR data
//Note that this will also automatically include SBAS data in the same file.
//
////////////////////////////////////////////////
void
ParseLog_ISMR( unsigned char* pucStr_, int iRequestedPrn_, FILE* fOut_, SYSTEM_TYPE eSystemChoice_ )
{
   int iIndex;
   int iNumObs;
   static bool       bFirstISMR = true;
   ISMR_CHANNEL_DATA sIsmrChanData_;
   HEADER_DATA       sIsmrHeaderData_;

   if (eSystemChoice_ == SYS_GPS) //ISMR includes only GPS & SBAS
   {
      if(bFirstISMR)
      {
         if (iRequestedPrn_ == JUST_AZ_EL)
            fprintf( fOut_, "Week, GPS TOW ,PRN,  Az  ,  Elv \n" );
         else
            fprintf( fOut_, "Week, GPS TOW ,PRN, RxStatus,   Az  ,  Elv ,L1 CNo, S4 , S4 Cor,1SecSigma,3SecSigma,10SecSigma,30SecSigma,60SecSigma, Code-Carrier, C-CStdev, TEC45, TECRate45, TEC30, TECRate30, TEC15, TECRate15, TEC0, TECRate0,L1 LockTime,ChanStatus,L2 LockTime, L2 CNo\n" );
          
         bFirstISMR = false;
         bIsmr = true;// flag ISMR log exists (global)
      }

      sIsmrHeaderData_ = *((HEADER_DATA*) &pucStr_[0]);
      iNumObs = pucStr_[sizeof(HEADER_DATA)];       

      for( iIndex = 0; iIndex < iNumObs; iIndex++ )
      {
         sIsmrChanData_  = *((ISMR_CHANNEL_DATA*) &pucStr_[sIsmrHeaderData_.ucHeaderLength+ 4 + iIndex*sizeof(ISMR_CHANNEL_DATA)]);
      
         if( iRequestedPrn_ == JUST_AZ_EL )
         {
            // Just print out PRNs, azimuth and elevations when input 'azel'
            fprintf( fOut_, "%4d, %10.3f, %2d, %6.2f, %5.2f\n",
                     sIsmrHeaderData_.usWeek,
                     sIsmrHeaderData_.ulMilliSecs/1000.0,
                     sIsmrChanData_.ulPrn,
                     sIsmrChanData_.fAzimuth,
                     sIsmrChanData_.fElevation );
         }
         else if( iRequestedPrn_ == ALL_PRNS || sIsmrChanData_.ulPrn == iRequestedPrn_ )
         {
            fprintf( fOut_, "%4d,  %9.2lf, %2d, %08X, %6.2f, %5.2f, %5.2lf, %lf, %lf, %lf, %lf, %lf, %lf, %lf, %lf, %.3lf, %f, %f, %f, %f, %f, %f, %f, %f, %.3lf, %08X, %.3lf, %5.2lf\n",
                     sIsmrHeaderData_.usWeek,
                     (double) sIsmrHeaderData_.ulMilliSecs/1000.0,
                     sIsmrChanData_.ulPrn,
                     sIsmrHeaderData_.ulRxStatus,
                     sIsmrChanData_.fAzimuth,
                     sIsmrChanData_.fElevation,
                     sIsmrChanData_.dCNo,
                     sIsmrChanData_.dS4,
                     sIsmrChanData_.dS4Correction,
                     sIsmrChanData_.d1SecSigma,
                     sIsmrChanData_.d3SecSigma,
                     sIsmrChanData_.d10SecSigma,
                     sIsmrChanData_.d30SecSigma,
                     sIsmrChanData_.d60SecSigma,
                     sIsmrChanData_.dCodeCarrier,
                     sIsmrChanData_.dCodeCarrierStdDev,
                     sIsmrChanData_.fTEC45,
                     sIsmrChanData_.fTECRate45,
                     sIsmrChanData_.fTEC30,
                     sIsmrChanData_.fTECRate30,
                     sIsmrChanData_.fTEC15,
                     sIsmrChanData_.fTECRate15,
                     sIsmrChanData_.fTEC0,
                     sIsmrChanData_.fTECRate0,
                     sIsmrChanData_.dLockTime,
                     sIsmrChanData_.ulStatus,
                     sIsmrChanData_.dL2LockTime,
                     sIsmrChanData_.dL2CNo );
         }
      }
   }
}

////////////////////////////////////////////////
//void ParseLog_REDOBS( ... )
//
//Parse a single instance of the ISMREDOBSB log, if the log contains data for the
//selected system, and write the formatted data into the output CSV file designated 
//for ISMREDOBS data
//
////////////////////////////////////////////////
void
ParseLog_REDOBS( unsigned char* pucStr_, unsigned long ulRequestedPrn_, FILE* fOut_, SYSTEM_TYPE eSystemChoice_  )
{
   unsigned long           i;
   static bool             bFirstOBS = true;
   ISMREDOBS_CHANNEL_DATA  sIsmrChanData_ ;
   HEADER_DATA             sIsmrHeaderData_;

   sIsmrHeaderData_ = *((HEADER_DATA*) &pucStr_[0]);
   if( bFirstOBS )
   {
      fprintf ( fOut_, "Phase and Amplitude Scintillation Indices\n\n");
      fprintf ( fOut_, "Satellite System: 0 = GPS, 1 = GLONASS, 2 = SBAS, 5 = GALILEO, 6 = COMPASS, 7 = QZSS, 8 = LBAND\n\n" );
      fprintf ( fOut_, "Frequency: GLONASS frequency channel (-7 to +6) \n\n");
      fprintf ( fOut_, "Signal Type for each Satellite System\n\n" );
      fprintf ( fOut_, "GPS     : 1 = L1CA,     4 = L2Y,  5 = L2C, 6 = L2P,    7 = L5Q\n");
      fprintf ( fOut_, "GLONASS : 1 = L1CA,     3 = L2CA, 4 = L2P\n");
      fprintf ( fOut_, "SBAS    : 1 = L1CA,     2 = L5I\n");					
      fprintf ( fOut_, "GALILEO : 1 = E1,       2 = E5A,  3 = E5B, 4 = ALTBOC, 5 = E6\n");
      fprintf ( fOut_, "COMPASS : 1 = E2\n");
      fprintf ( fOut_, "QZSS    : 1 = L1CA,     3 = L2C,  4 = L5Q\n");
      fprintf ( fOut_, "LBAND   : 1 = OMNISTAR, 2 = CDGPS\n\n");	       fprintf  ( fOut_, "GPS Week: %4d, ", sIsmrHeaderData_.usWeek);
      fprintf ( fOut_, " Satellite System: %d", eSystemChoice_);
       
      if (ulRequestedPrn_ == JUST_AZ_EL)
         fprintf ( fOut_, "\n\nGPS TOW , PRN, Freq, SigType, Az  ,  Elv \n" );
      else
         fprintf ( fOut_, "\n\nGPS TOW , PRN, Freq, SigType, Az , Elv , CNo , Lock Time, CMC Avg, CMC Std , S4 , S4 Cor, 1SecSigma, 3SecSigma, 10SecSigma, 30SecSigma, 60SecSigma \n");

      bFirstOBS = false;
      bRedObs = true; //flag if Reduced Observation log exists
   }
   
   unsigned long svn = pucStr_[sizeof(HEADER_DATA)];

   for(i = 0; i < svn; i++)
   {
      sIsmrChanData_  = *((ISMREDOBS_CHANNEL_DATA*) &pucStr_[sIsmrHeaderData_.ucHeaderLength+4 + i*sizeof(ISMREDOBS_CHANNEL_DATA)]);

      if(sIsmrChanData_.ucSvSys == eSystemChoice_)
      {
         if( ulRequestedPrn_ == JUST_AZ_EL )
         {
            // Just print out azimuth and elevations when input PRN = 0
            fprintf( fOut_, " %9.2lf, %d, %d, %d, %6.2f, %5.2f \n",
                     (double) sIsmrHeaderData_.ulMilliSecs/1000.0,
                     sIsmrChanData_.ucPrn,
                     sIsmrChanData_.cFreq,
                     sIsmrChanData_.ucSigType,
                     sIsmrChanData_.fAzimuth,
                     sIsmrChanData_.fElevation);
         }
         else if( ulRequestedPrn_ == ALL_PRNS || sIsmrChanData_.ucPrn == ulRequestedPrn_)
         {
            fprintf( fOut_, "%9.2lf,%d,%d,%d, %6.2f,%5.2f,%5.2lf,%lf,%.3lf,%.3lf,%lf,%lf,%lf,%lf,%lf,%lf,%lf \n",
                     (double) sIsmrHeaderData_.ulMilliSecs/1000.0,
                     sIsmrChanData_.ucPrn,
                     sIsmrChanData_.cFreq,
                     sIsmrChanData_.ucSigType,
                     sIsmrChanData_.fAzimuth,
                     sIsmrChanData_.fElevation,
                     sIsmrChanData_.fCNo,
                     sIsmrChanData_.fLockTime,
                     sIsmrChanData_.fCMCAvrg,
                     sIsmrChanData_.fCMCStd,
                     sIsmrChanData_.fS4,
                     sIsmrChanData_.fS4Correction,
                     sIsmrChanData_.f1SecSigma,
                     sIsmrChanData_.f3SecSigma,
                     sIsmrChanData_.f10SecSigma,
                     sIsmrChanData_.f30SecSigma,
                     sIsmrChanData_.f60SecSigma );
         }
      }
   }
}

////////////////////////////////////////////////
//void ParseLog_REDTEC( ... )
//
//Parse a single instance of the ISMREDTECB log, if the log contains data for the
//selected system, and write the formatted data into the output CSV file designated 
//for ISMREDTEC data
//
////////////////////////////////////////////////
void
ParseLog_REDTEC( unsigned char* pucStr_, unsigned long ulRequestedPrn_, FILE* fOut_, SYSTEM_TYPE eSystemChoice_  )
{
   int                      iIndex;
   int                      iSVN;
   static bool              bFirstTEC = true;
   ISMREDTEC_CHANNEL_DATA   sIsmrChanData_;
   HEADER_DATA              sIsmrHeaderData_;

   sIsmrHeaderData_ = *((HEADER_DATA*) &pucStr_[0]);
   
   if( bFirstTEC )
   {
      fprintf ( fOut_, "TEC and TEC Rate\n\n" );
      fprintf ( fOut_, "Satellite System: 0 = GPS, 1 = GLONASS, 2 = SBAS, 5 = GALILEO, 6 = COMPASS, 7 = QZSS, 8 = LBAND\n\n" );
      fprintf ( fOut_, "Frequency: GLONASS frequency channel (-7 to +6) \n\n" );
      fprintf ( fOut_, "Signal Type for each Satellite System\n\n" );
      fprintf ( fOut_, "GPS     : 1 = L1CA,     4 = L2Y,  5 = L2C, 6 = L2P,    7 = L5Q\n");
      fprintf ( fOut_, "GLONASS : 1 = L1CA,     3 = L2CA, 4 = L2P\n");
      fprintf ( fOut_, "SBAS    : 1 = L1CA,     2 = L5I\n");					
      fprintf ( fOut_, "GALILEO : 1 = E1,       2 = E5A,  3 = E5B, 4 = ALTBOC, 5 = E6\n");
      fprintf ( fOut_, "COMPASS : 1 = E2\n");
      fprintf ( fOut_, "QZSS    : 1 = L1CA,     3 = L2C,  4 = L5Q\n");
      fprintf ( fOut_, "LBAND   : 1 = OMNISTAR, 2 = CDGPS\n\n");	           fprintf ( fOut_, "GPS Week: %4d,", sIsmrHeaderData_.usWeek);
      fprintf ( fOut_, "  Satellite System: %d", eSystemChoice_);
      if (ulRequestedPrn_ != JUST_AZ_EL)
      {      
         fprintf ( fOut_, "\n\nGPS TOW,PRN, Freq, PrimSig, SecSig, Azimuth, Elev, SecSig Lock Time, SecSig CNo,TEC15, TECRate15, TEC30, TECRate30, TEC45, TECRate45, TECTOW, TECRateTOW\n" );
      }
      else
      {
         fprintf ( fOut_, "\n\nGPS TOW, System, PRN, Freq, PrimSig, SecSig, Azimuth, Elev\n" );
      }
		
      bFirstTEC = false;
      bRedTEC   = true;//flag if reduced TEC exist
   }


   iSVN = pucStr_[sizeof(HEADER_DATA)];
   
   for( iIndex = 0; iIndex < iSVN; iIndex++)
   {
      sIsmrChanData_  = *((ISMREDTEC_CHANNEL_DATA*) &pucStr_[sIsmrHeaderData_.ucHeaderLength+4 + iIndex*sizeof(ISMREDTEC_CHANNEL_DATA)]);
          
      if(sIsmrChanData_.ucSvSys == eSystemChoice_)
      {
         if( ulRequestedPrn_ == ALL_PRNS || ulRequestedPrn_ == JUST_AZ_EL || sIsmrChanData_.ucPrn == ulRequestedPrn_)
         {
            if (ulRequestedPrn_ != JUST_AZ_EL)
            {
               fprintf( fOut_, " %9.2lf, %d, %d, %d, %d, %f, %f, %lf, %.3lf, %lf, %lf, %lf,%lf, %lf, %lf, %lf, %lf \n",				  
                        (double) sIsmrHeaderData_.ulMilliSecs/1000.0,
                        sIsmrChanData_.ucPrn,
                        sIsmrChanData_.cFreq,
                        sIsmrChanData_.ucPrimSignal,
                        sIsmrChanData_.ucSecSignal,
                        sIsmrChanData_.fAzimuth,
                        sIsmrChanData_.fElevation,
                        sIsmrChanData_.fSecSigLckTime,
                        sIsmrChanData_.fSecSigCNo,
                        sIsmrChanData_.fTEC15,
                        sIsmrChanData_.fdTEC15,
                        sIsmrChanData_.fTEC30,
                        sIsmrChanData_.fdTEC30,
                        sIsmrChanData_.fTEC45,
                        sIsmrChanData_.fdTEC45,
                        sIsmrChanData_.fTECTOW,
                        sIsmrChanData_.fdTECTOW );
            }
            else
            {
                  fprintf( fOut_, " %9.2lf, %d, %d, %d, %d, %f, %f\n",				  
                        (double) sIsmrHeaderData_.ulMilliSecs/1000.0,
                        sIsmrChanData_.ucPrn,
                        sIsmrChanData_.cFreq,
                        sIsmrChanData_.ucPrimSignal,
                        sIsmrChanData_.ucSecSignal,
                        sIsmrChanData_.fAzimuth,
                        sIsmrChanData_.fElevation);
            }
         }
      }
   }
}

////////////////////////////////////////////////
//unsigned long CRC32Value( ... )
////////////////////////////////////////////////
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

////////////////////////////////////////////////
//bool CheckCrcOk( ... )
//
//Parse CRC to ensure no log corruption
////////////////////////////////////////////////
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

////////////////////////////////////////////////
//void ScanForLogs( ... )
//
//Scan through the entire supplied input file, seeking logs that match user's input criteria.
//Terminate this function only when we reach the end of file
////////////////////////////////////////////////
void
ScanForLogs( FILE* fIn_, int iPrn_, FILE* fOut_, FILE* fOBS_, FILE* fTEC_, SYSTEM_TYPE eSystemChoice_)
{
   unsigned char  aucParseString[MAX_LOG_SIZE];
   unsigned char  aucFileBuffer[MAX_BUFFER_SIZE];
   unsigned char  aucTempFileBuffer[MAX_BUFFER_SIZE];
   unsigned char  ucHeaderLength;
   unsigned long  ulMessageID;
   unsigned long  ulMessageLength;
   int            iLogCountRedObs = 0;
   int            iLogCountRedTec = 0;
   int            iLogCountIsmr = 0;
   int            iBufferPtr = NULL;
   int            iBytesRead = 0;
   int            iBufferSize = 0;
   bool           bFileExhausted = false;
   
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
               //Got through full preamble; evaluate whether or not this log is supported
               //and parse it if it is
               aucParseString[3] = aucFileBuffer[iBufferPtr++];
               ucHeaderLength    = aucParseString[3];
               aucParseString[4] = aucFileBuffer[iBufferPtr++];
               aucParseString[5] = aucFileBuffer[iBufferPtr++];
               ulMessageID       = (unsigned long) aucParseString[4] | ((unsigned long)aucParseString[5] << 8);
               aucParseString[6] = aucFileBuffer[iBufferPtr++]; // Message Type
               aucParseString[7] = aucFileBuffer[iBufferPtr++]; // Port Address
               aucParseString[8] = aucFileBuffer[iBufferPtr++];
               aucParseString[9] = aucFileBuffer[iBufferPtr++];
               ulMessageLength = (unsigned long) aucParseString[8] | ((unsigned long)aucParseString[9] << 8);

               // Log messages supported...
               // ISMREDOBS (1393), ISMREDTEC (1394) and ISMR (274)
               if( ulMessageID == 0x112 
                   || ulMessageID == 0x571 
                   || ulMessageID == 0x572
                   && ulMessageLength < MAX_LOG_SIZE)
               {
                  
				   if( iLogCountRedObs % 10 == 1 && ulMessageID == 0x571 )
                     printf("Parsed %i ISMREDOBS logs (= %f hours)\n", iLogCountRedObs, iLogCountRedObs/60.0);
                  if( iLogCountRedTec % 10 == 1 && ulMessageID == 0x572)
                     printf("Parsed %i ISMREDTEC logs (= %f hours)\n", iLogCountRedTec, iLogCountRedTec/60.0);
                  if( iLogCountIsmr % 10 == 1  && ulMessageID == 0x112)
                     printf("Parsed %i ISMR logs (= %f hours)\n", iLogCountIsmr, iLogCountIsmr/60.0);

                  for(int i=0; i < (ulMessageLength + ucHeaderLength - 6); i++)
                  {
                     aucParseString[i+10] = aucFileBuffer[iBufferPtr++];
                  }

                  if( CheckCrcOk( &aucParseString[0], ulMessageLength + ucHeaderLength + 4 ) )
                  {
                     if (ulMessageID == 0x112 )
                     {
                        ParseLog_ISMR( &aucParseString[0], iPrn_, fOut_ , eSystemChoice_);     // ISMR (274)
                        iLogCountIsmr++;
                     }
                     else if (ulMessageID == 0x571)
                     {
                        ParseLog_REDOBS( &aucParseString[0], iPrn_, fOBS_ , eSystemChoice_);  // ISMREDOBS (1393)
                        iLogCountRedObs++;
                     }
                     else if (ulMessageID == 0x572)
                     {
                        ParseLog_REDTEC( &aucParseString[0], iPrn_, fTEC_, eSystemChoice_ );  // ISMREDTEC (1394)
                        iLogCountRedTec++;
                     }
                  }
               }
               else
               {
                  //Valid message, but not supported so let's skip to the next one
                  iBufferPtr += (ulMessageLength + ucHeaderLength - 6);
               }
            }
            else
            {
               //Preamble doesn't check out; back up and try the next character
               iBufferPtr -= 2;
            }
         }
         else
         {
            //Preamble doesn't check out; back up and try the next character
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
}

int main( int argc, char* argv[] )
{
   int           iPrn = JUST_AZ_EL;
   char*         pcPRNSelector;
   
   SYSTEM_TYPE   eSystemChoice;
   char*         szInFileName;
   char*         szOutFileName;
   char          szOut_REDOBS_file[MAX_OUTFILE_NAME];//Reduced Observation
   char          szOut_REDTEC_file[MAX_OUTFILE_NAME];//Reduced TEC
   char          szOut_ISMR_file  [MAX_OUTFILE_NAME];//ISMR
   int           err, n_file;
   FILE*         fIn;
   FILE*         fOut_ISMR;
   FILE*         fOut_REDOBS;
   FILE*         fOut_REDTEC;
     
   printf("\nGPStation-6 Reduced Observation Post-Processing Utility\n");
#if ATNOVATEL
   //More detailed version information based on NovAtel's VCS
   PrintVersion();
#endif

   if( argc == 4 )
   {
      szInFileName  = argv[2];
      szOutFileName = argv[3];

        //System and PRN
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
          //User has entered 0, indicating only Az/El for all SVs is needed
          //No system type is selected, but this is a valid entry
          fprintf(stderr, "Invalid System chosen for selected PRN\r\n");
          Usage();
      default:
          fprintf(stderr, "Invalid System chosen for selected PRN\r\n");
          Usage();
      }
   }
   else
   {
      Usage();
   }
   if (strlen(pcPRNSelector) == 1)
      iPrn = ALL_PRNS;                  //User entered only a System, output all PRN for that system
   else if(strlen(pcPRNSelector) > 1)
      iPrn = atol( &pcPRNSelector[1] ); //User entered a system & value, invalide PRN number defaults to 0
      
   //Open input file
   err = fopen_s(&fIn, szInFileName, "rb");
   if( err != 0 )
   {
      fprintf(stderr, "Can't open file: %s\r\n", szInFileName );
      Usage();
   }

   //Append log name keywords for log-specific output files
   strcpy_s(szOut_ISMR_file,"ISMR_");
   strcat_s(szOut_ISMR_file,szOutFileName);
   strcpy_s(szOut_REDOBS_file,"REDOBS_");
   strcat_s(szOut_REDOBS_file,szOutFileName);
   strcpy_s(szOut_REDTEC_file,"REDTEC_");
   strcat_s(szOut_REDTEC_file,szOutFileName);
   
   //Open and check output files
   err = fopen_s( &fOut_ISMR, szOut_ISMR_file, "wb" );
   if( err != 0 )
   {
      fprintf(stderr, "Can't open file: %s, file may be open\r\n", szOut_ISMR_file );
      Usage();
   }
   err = fopen_s( &fOut_REDOBS, szOut_REDOBS_file, "wb" );
   if( err != 0 )
   {
      fprintf(stderr, "Can't open file: %s, file may be open\r\n", szOut_REDOBS_file );
      Usage();
   }
   err = fopen_s( &fOut_REDTEC, szOut_REDTEC_file, "wb" );
   if( err != 0 )
   {
      fprintf( stderr, "Can't open file: %s, file may be open\r\n", szOut_REDTEC_file );
      Usage();
   }
   
   //Parse everything!
   ScanForLogs( fIn, iPrn, fOut_ISMR, fOut_REDOBS, fOut_REDTEC, eSystemChoice );

   n_file =_fcloseall();
   // remove files which contain no data
   if (!bIsmr)remove(szOut_ISMR_file);
   if (!bRedObs)remove(szOut_REDOBS_file);
   if (!bRedTEC)remove(szOut_REDTEC_file);
   
   return 0;
}
