#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include "sndfile.h"
#include "fftw3.h"
#include <sys/soundcard.h>

#include "spsvcomm.h"

#define MIN(X,Y) ((X) < (Y) ? (X) : (Y))

#define SAMPLE_RATE   44100
#define WINDOW_SIZE   (44100>>1)
#define FRAC_READ 0
#define LARGEST_SHORT 32767


#define PI 3.1415927

#define PI_2 2*PI
#define PI_4 4*PI

#define BM_WINDOW(X) (.42 - .5*cos(PI_2*(X)/(WINDOW_SIZE-1)) +	\
		      .08*cos(PI_4*(X)/(WINDOW_SIZE-1)))

#define FFT_IN(val, index) (((double)(val))*BM_WINDOW((index))/LARGEST_SHORT)
/*#define FFT_IN(val, index) (((double)(val))/LARGEST_SHORT)*/

/*
 * Jeff Kaufman, 2008 (GPL)
 *
 * Some portions derived from FFTW demo from captain.at, some portions
 * derived from OSS API reference
 *
 *
 */

/* Open the audio device with name "name" for reading.  Exit under
 * various failure conditions.  Sets it for mono reading of 16 bit
 * samples at SAMPLE_RATE */
int open_auddev (char* name)
{
   int tmp, fd, sample_rate;
   
   if ((fd = open (name, O_RDONLY, 0)) == -1)
   {
      perror (name);
      exit (-1);
   }

   tmp = AFMT_S16_NE;/* Native 16 bits */
   if (ioctl (fd, SNDCTL_DSP_SETFMT, &tmp) == -1)
   {
      perror ("SNDCTL_DSP_SETFMT");
      exit (-1);
   }

   if (tmp != AFMT_S16_NE)
   {
      fprintf (stderr,
	       "The device doesn't support the 16 bit sample format.\n");
      exit (-1);
   }

   tmp = 1;
   if (ioctl (fd, SNDCTL_DSP_CHANNELS, &tmp) == -1)
  {
      perror ("SNDCTL_DSP_CHANNELS");
      exit (-1);
   }

   if (tmp != 1)
   {
      fprintf (stderr, "The device doesn't support mono mode.\n");
      exit (-1);
   }

   sample_rate = SAMPLE_RATE;
   if (ioctl (fd, SNDCTL_DSP_SPEED, &sample_rate) == -1)
   {
      perror ("SNDCTL_DSP_SPEED");
      exit (-1);
   }

   return fd;
}

/* convert unwindowed from short to double and window it */
void do_window(short* unwindowed, double* windowed)
{
   int i;

   for(i = 0 ; i < WINDOW_SIZE ; i++)
      windowed[i] = FFT_IN(unwindowed[i], i); 
}

/* stupid function -- proper crcular buffer would do away with this */
void advance_buf(short* buf, int amt_advance)
{
   int i;
   for(i = 0 ; i < WINDOW_SIZE - amt_advance ; i++)
      buf[i] = buf[i+amt_advance];
   for(i = WINDOW_SIZE - amt_advance ; i < WINDOW_SIZE ; i++)
      buf[i] = 0;
}

/* put num_samples at the end of buf */
void fill_buf(int fd, short* buf, int num_samples)
{
   int amt = 0;
   int incr = 0;

   int offset = WINDOW_SIZE - num_samples;

   while(amt < num_samples)
   {
      //printf("Reading %d samples into buf at offset %d.\n",
      //     num_samples - amt, offset + amt);
      incr = read(fd, buf + offset + amt, num_samples - amt);
      if (incr == -1)
      { 
	 perror ("buffer fill fail");  
	 exit (-1); 
      }
      amt += incr;      
   }
}

void sense(int aud_fd, struct spsv_commobj* sc)
{
   short mic_buf[WINDOW_SIZE];  /* mic output */

   double* sound; /* fft input */
   double* freq;  /* fft output */
   fftw_plan p;   /* fftw data to turn sound into freq */

   FILE* file;

   /* fft input */
   sound = (double*) fftw_malloc( sizeof(double) * WINDOW_SIZE);

   /* fft output */
   freq = (double*) fftw_malloc( sizeof(double) * WINDOW_SIZE);
   
   p = fftw_plan_r2r_1d(WINDOW_SIZE, sound, freq,
			FFTW_R2HC, FFTW_FORWARD);
   
   printf("Set up, about to process sound\n");

   char erg[256];
   sprintf(erg, "data.dat");
   file = fopen(erg, "w");

   fill_buf(aud_fd, mic_buf, WINDOW_SIZE);

   printf("About to loop.\n");

   int cycle = 0;
   while(1)
   {
      do_window(mic_buf, sound); /* convert input to doubles and
				  * window it */
      fftw_execute(p);

      send_data(sc, WINDOW_SIZE/2-1, freq);

      advance_buf(mic_buf, WINDOW_SIZE >> FRAC_READ);

      fill_buf(aud_fd, mic_buf, WINDOW_SIZE>>FRAC_READ);

      cycle ++;
   }
   
   printf("Done with sound, about to close up\n");

   fclose(file);

   fftw_destroy_plan(p);
   fftw_free(sound);
   fftw_free(freq);
}

/* args:
 *
 * 1: Port to listen on
 * 2: Device name of sound card
 *
 */
int main(int argc, char** argv)
{
   char* dev_name;
   int aud_fd;
   struct spsv_commobj sc;

   if (argc != 2)
   {
      printf("Usage: specserver <devname>\n");
      exit(-1);
   }
   dev_name = argv[1];

   aud_fd = open_auddev(dev_name);

   printf("Audio device opened, waiting for contact\n");

   build_commobj(&sc);
   wait_for_request_transmission(&sc);

   sense(aud_fd, &sc);

   return 1;
}
