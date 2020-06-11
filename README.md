# Mangle

## Overview 
This repository is for understanding and using GLibC 2.32 with the pointer mangling that has been added.   
These new security mitigations make exploitation harder but not impossible. For details on the mangling and   
alignment fixes, check out: https://research.checkpoint.com/2020/safe-linking-eliminating-a-20-year-old-malloc-exploit-primitive/  
  
What's in here? 
- Pointer mangling and unmangling functions
- Decoder of mangled pointers
- LibC and Loader binary with Malloc that has pointer mangling implemented. 
- Both functions and CLI for executions the above functionality 
- Modified Malloc_Playground (how2heap style) that has a premade Python interface in order to make testing easier
- Example usage of functions with working examples for memory corruption

For a write up explaining the implications of these security mitigations and how they work, please visit TODO.

## Files 
- mangle.py: 
	- The script with all pointer mangling functions
- fake_chunk.py: 
	- Example usage of the functions and interface with 
          malloc_playground functions
- malloc_playground.c: 
	- A easy way to test the functionality of malloc
- libc.so: 
	- A compiled version of GLibC 2.32 with the   
          added pointer mangling protections 
- ld-linux-x86-64.so.2: 
	- The loader for the libc binary 

## CLI Docs 
There are only four functions in the file to use: 
- encode_ptr - Mangles a pointer 
	- fd_ptr: Takes in the *fd pointer* to be mangled
	- storage_location: Takes in the *storage location* of the ptr
- decode_ptr - Demangles a pointer
	- mangled_ptr: Takes in the currently mangled *fd pointer*
	- storage_location: Takes in the *storage location* of the ptr
- recover_ptr - Recovers the storage loc and fd ptr from a mangled ptr
	- mangled_ptr: Takes in the currently mangled ptr 
	- loc_final_bits: Takes in the final 12 bits of the location ptr
- showcase - Example usage of the functions

This uses Python Fire, making it super easy to use. Example usage of encode_ptr: 
```
python mangle.py encode_ptr --fd_ptr 0x987654321 --storage_location 0x987654987
```
or (less details)
```
python mangle.py encode_ptr 0x987654321 0x987654987
```

## Function Usage 
The usage of the functions is described above (from the CLI docs). 
There is also documentation on the functions itself within the `mangle.py` file. 

To import the functions (with a file in the same directory as mangle.py), just use 
```
from mangle import *
```

## Future 
Overall, my main goal was to just write a blog post about this and include something for people to easily play with.  
In the future, this type of stuff will need to be included in awesome debuggers (gef and pwndbg) and any type of pwn dealing  
with GLibC 2.32 or greater.   
  
For the time being, feel free to contribute to this repository to add better examples, more functionality, fix any bugs or anything else that you feel would be helpful!

## Edits
- My original implementation of the recover_ptrs function made a bad assumption with a parameter called *offsets*. Although it worked some of the time (depending on the new ptrs), it was consistent and not mathmatically sound. So, this was removed.
