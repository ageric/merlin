#include "shared.h"
#include "hookinfo.h"

/*
 * Both of these conversions involve a fair deal of Black Magic.
 * If you don't understand what's happening, please don't fiddle.
 *
 * For those seeking enlightenment, read on:
 * The packet must be a single continuous block of memory in order
 * to be efficiently sent over the network. In order to arrange
 * this, we must handle strings somewhat specially.
 *
 * Each string is copied to the "free" memory area beyond the rest
 * of the data contained in the object we're mangling, one* after
 * another and will a single nul char separating them. The pointers
 * to the strings are then modified so they contain the relative
 * offset from the beginning of the memory area instead of an
 * absolute memory address.  This means that in order to use those
 * strings once a packet has been encoded, it must be decoded again
 * so the string pointers are restored to an absolute address,
 * calculated based on the address of the base object and their
 * relative offset regarding that base object.
 *
 * One way to access a string inside an encoded object without
 * first running it through merlin_encode is to use:
 *
 *   str = buf->some_string + (unsigned long)buf);
 *
 * but that quickly gets unwieldy, is harder to test automagically
 * and means callers must be aware of implementation details they
 * shouldn't really have to care about, so we avoid that idiom.
 */

/*
 * Fixed-length variables are simply memcpy()'d.
 * Each string allocated is stuck in a memory area at the end of
 * the object. The pointer offset is then set to reflect the start
 * of the string relative to the beginning of the memory chunk.
 */
int merlin_encode(void *data, int cb_type, char *buf, int buflen)
{
	int i, len, strings;
	off_t off, *ptrs;

	if (!data || cb_type < 0 || cb_type >= NEBCALLBACK_NUMITEMS)
		return 0;

	off = hook_info[cb_type].offset;
	strings = hook_info[cb_type].strings;
	ptrs = hook_info[cb_type].ptrs;

	memcpy(buf, data, off);

	for(i = 0; i < strings; i++) {
		char *sp;

		memcpy(&sp, (char *)buf + ptrs[i], sizeof(sp));
		if (!sp) {	/* NULL pointers remain NULL pointers */
			continue;
		}

		/* check this after !sp. No need to log a warning if only
		 * NULL-strings remain */
		if (buflen <= off) {
			lwarn("No space remaining in buffer. Skipping remaining %d strings",
				  strings - i);
			break;
		}
		len = strlen(sp);

		if (len > buflen - off) {
			linfo("String is too long (%d bytes, %lu remaining). Truncating",
				  len, buflen - off);
			len = buflen - off;
		}

		/* set the destination pointer */
		if (len)
			memcpy(buf + off, sp, len);

		/* nul-terminate the string. This way we can determine
		 * the difference between NULL pointers and nul-strings */
		buf[off + len] = '\0';

		/* write the correct location back to the block */
		memcpy(buf + ptrs[i], &off, sizeof(off));

		/* increment offset pointers and decrement remaining space */
		off += len + 1;
	}

	return off;
}


/*
 * Undo the pointer mangling done above (well, not exactly, but the
 * string pointers will point to the location of the string in the
 * block anyways, and thus "work").
 * Note that strings still cannot be free()'d, since the memory
 * they reside in is a single continuous block making up the entire
 * event.
 */
int merlin_decode(void *ds, off_t len, int cb_type)
{
	off_t *ptrs;
	int strings, i;

	if (!ds || !len || cb_type < 0 || cb_type >= NEBCALLBACK_NUMITEMS)
		return 0;

	strings = hook_info[cb_type].strings;
	ptrs = hook_info[cb_type].ptrs;

	for (i = 0; i < strings; i++) {
		char *ptr;

		if (!ptrs[i]) {
			lwarn("!ptrs[%d]; strings == %d. Fix the hook_info struct", i, strings);
			continue;
		}

		/* get the relative offset */
		memcpy(&ptr, (char *)ds + ptrs[i], sizeof(ptr));

		if (!ptr) /* ignore null pointers from original struct */
			continue;

		/* make sure we don't overshoot the buffer */
		if ((off_t)ptr > len) {
			lerr("Nulling OOB ptr %u. type: %d; offset: %p; len: %lu; overshot with %lu bytes",
				 i, *(int *)ds, ptr, len, (off_t)ptr - len);

			ptr = NULL;
		}
		else
			ptr += (off_t)ds;

		/* now write it back to the proper location */
		memcpy((char *)ds + ptrs[i], &ptr, sizeof(ptr));
	}

	return 1;
}