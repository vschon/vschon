// copyright 2013 Brandon

#pragma once

#include <stdint.h>
#include <assert.h>
#include <stdlib.h>

#include <sched.h>

#define SwitchToThread() sched_yield()
// the sched_yield forces the running thread to relinquish the processor
// until it becomes the head of thread list
// for linux only
#include <malloc.h>

#define InterlockedBoolCompareExchange(A, B, C) __sync_bool_compare_and_swap(A, C, B) 
// compare A and C, if not equal, set A = B 

#define _InterlockedExchange(A, B) (long)__sync_lock_test_set(A, B)
// assign value B to A

#define InterlockedBoolExchange(A, B) (_InterlockedExchange(A, B) == (B))

#define InterlockedIncrement(A) (long)__sync_add_and_fetch(A, 1L)
#define InterlockedDecrement(A) (long)__sync_sub_and_fetch(A, 1L)
