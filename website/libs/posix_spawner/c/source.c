#include <sys/types.h>
#include <spawn.h>
#include <signal.h>

void noZombies(void)
{
  struct sigaction arg = {
    .sa_handler=SIG_IGN,
    .sa_flags=SA_NOCLDWAIT   // never wait for a child. 
  };
  sigaction( SIGCHLD, &arg, NULL );
}
