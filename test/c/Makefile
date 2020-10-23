CC			:= gcc
PRJ			:= test.elf

INC_C		:= /home/veba/github/cody/test/c/libb/include

SRC_C		:= /home/veba/github/cody/test/c/main.c /home/veba/github/cody/test/c/test.c /home/veba/github/cody/test/c/libb/libb.c /home/veba/github/cody/test/c/liba/liba.c

OBJS		:= $(SRC_C:.c=.o)



.c.o:
	$(CC) -c ${CFLAGS} ${INC_C} $< -o $@

all: $(OBJS)
	 $(CC) ${LDFLAGS} ${INC_LIB} -o $(PRJ) ${OBJS} ${LIBS}
clean:
	 rm -rf $(PRJ) $(OBJS)