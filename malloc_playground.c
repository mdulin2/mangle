#include <inttypes.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#ifdef __GLIBC__
# include <malloc.h>
# include <mcheck.h>

/*
Taken from how2heap and slightly modified to add the 'write' case. 
To use for the demo, compile with the following: 

gcc -g -Wl,-z,relro malloc_playground.c -o playground2 -pie -fPIC

Then, patch the interpreter on the binary with the following: 

patchelf --set-interpreter "$PWD/ld-linux-x86-64.so.2" ./playground2

Now, feel free to play around on the playground!
*/
void print_mcheck_status(enum mcheck_status s)
{
	fprintf(stderr, "%s\n", (s == MCHECK_DISABLED) ? "N/A, you didn't enable mcheck()" :
				   (s == MCHECK_OK) ? "No inconsistency detected" :
				   (s == MCHECK_HEAD) ? "Memory preceding an allocated block was clobbered" :
				   (s == MCHECK_TAIL) ? "Memory following an allocated block was clobbered" :
				   (s == MCHECK_FREE) ? "A block of memory was freed twice" :
				   "unknown memory check code!");
}
void report_mcheck_fail(enum mcheck_status s)
{
	fprintf(stderr, "*** PROGRAM WOULD ABORT: "); print_mcheck_status(s);
}
#endif

int main(int argc, char ** argv) {

	fprintf(stderr, "pid: %d\n", getpid());

	char buffer[1000];
	while (1) {
		fprintf(stderr, "> ");
		fgets(buffer, sizeof(buffer), stdin);
		char cmd[1000];
		intptr_t arg1, arg2;
		int num = sscanf(buffer, "%s %"SCNiPTR" %"SCNiPTR, cmd, &arg1, &arg2);
		if (strcmp(cmd, "malloc") == 0) {
			void* result = malloc(arg1);
			fprintf(stderr, "==> %p\n", result);
		} else if (strcmp(cmd, "free") == 0) {
			free((void*) arg1);
			fprintf(stderr, "==> ok\n");
		} else if (strcmp(cmd, "show") == 0) {
			if (num == 2) {
				arg2 = 1;
			}
			long * src = (long*) arg1;
			for (int i = 0; i < arg2; i++) {
				fprintf(stderr, "%p: %#16.0lx\n", &src[i], src[i]);
			}

		} else if (strcmp(cmd, "write") == 0){
			fprintf(stderr, "Data to write: ");
			read(0,((long *)arg1) + (int)arg2,9);
		} else if(strcmp(cmd, "libc") == 0){
			printf("System Ptr: %p\n", &system);
#ifdef __GLIBC__
		} else if (strcmp(cmd, "usable") == 0) {
			fprintf(stderr, "usable size: %zu\n", malloc_usable_size((void*) arg1));
		} else if (strcmp(cmd, "stats") == 0) {
			malloc_stats();
		} else if (strcmp(cmd, "info") == 0) {
			malloc_info(0, stdout);
		} else if (strcmp(cmd, "mcheck") == 0) {
			fprintf(stderr, "==> %s\n", mcheck(report_mcheck_fail) == 0 ? "OK" : "ERROR");
		} else if (strcmp(cmd, "mcheck_pedantic") == 0) {
			fprintf(stderr, "==> %s\n", mcheck_pedantic(report_mcheck_fail) == 0 ? "OK" : "ERROR");
		} else if (strcmp(cmd, "mprobe") == 0) {
			if (num > 1) {
				print_mcheck_status(mprobe((void*) arg1));
			} else {
				mcheck_check_all();
				fprintf(stderr, "==> check_all ok\n");
			}
#endif
		} else {
			puts("Commands: malloc n, free p, show p [n], write p index, libc, usable p, stats, info, mprobe [p], mcheck, mcheck_pedantic");
		}
	}
}
