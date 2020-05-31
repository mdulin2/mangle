# Mangle

## Overview 
This repository is for understanding and using GLibC 2.32 with the pointer mangling that has been added.   
These new security mitigations make exploitation harder but not impossible. For details on the mangling and   
alignment fixes, check out: https://research.checkpoint.com/2020/safe-linking-eliminating-a-20-year-old-malloc-exploit-primitive/  
  
For a write up explaining the implications of these patches, please visit TODO.

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
	- offset: Takes in the offset between mangled_ptr and the location
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


