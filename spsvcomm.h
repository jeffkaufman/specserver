/* functions for the UDP communication part of the service
 *
 * protocol (UDP based):
 * 1) Client sends "Request transmission" packet
 *    - 2 bytes, defined in REQUEST_TRANSMISSION
 * 2) Server starts sending data
 *    - index (unsigned int, 4 bytes)
 *    - data  (floats, 4 bytes each)
 */ 

#include <stdio.h>
#include <netinet/in.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/socket.h>


#define REQUEST_TRANSMISSION 0x2AF6
#define SPSVCOMM_PORTNUM       8843
#define SQUARE(X) ((X)*(X))

struct spsv_commobj
{
      int fd;
      unsigned int slen;
      struct sockaddr_in my_addr;
      struct sockaddr_in their_addr;
};

void do_or_die(int val, char* msg)
{
   if(val == -1)
   {
      perror(msg);
      exit(-1);
   }
}

void build_commobj(struct spsv_commobj* sc)
{
   sc->slen = sizeof(struct sockaddr_in);

   sc->my_addr.sin_port = htons(SPSVCOMM_PORTNUM);
   sc->my_addr.sin_family = PF_INET;
   sc->my_addr.sin_addr.s_addr = htonl(INADDR_ANY);

   do_or_die(sc->fd = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP),
	     "socket()");

   do_or_die(bind(sc->fd, (struct sockaddr*)&(sc->my_addr),
		  sc->slen), "bind()");
}

void wait_for_request_transmission(struct spsv_commobj* sc)
{
   short data;
   
   do
   {
      data = 0;
      do_or_die(recvfrom(sc->fd, (char*)&data,
			    sizeof(data), 0,
			    (struct sockaddr*)&(sc->their_addr),
			    &(sc->slen)),
		"server listen");
      printf("Recieved data\n");
   } while(data != REQUEST_TRANSMISSION);
   printf("Got good connection\n");
}

/* break the data down into packets and send them off */
void send_data(struct spsv_commobj* sc,
	       int len,
	       double* data)
{
   /* assert(sizeof(float) == sizeof(int) == 4) */

   int packet_len = 508/4;
   int packets_sent = 0;
   char buf[packet_len*4];
   unsigned int data_idx = 0;

   int i;

   for(packets_sent = 0 ; data_idx < len ; packets_sent++)
   {
      ((unsigned int*) buf)[0] = data_idx;
      for(i = 1; i < packet_len && data_idx < len; i++, data_idx++)
	 ((float*)buf)[i] 
	    = (float)SQUARE(data[data_idx]);

      do_or_die(sendto(sc->fd, buf, i*4, 0,
		       (struct sockaddr*)&(sc->their_addr),
		       sc->slen),
		"sending datagram");
   }
}
