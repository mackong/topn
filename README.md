# Introduction
A simple program to calculate topn of most occured urls in a large file (100GB) which cannot be loaded into memory (1GB) directly.

# Usage
## generate test data
```
make data
```

## test with 1GB urls
```
make test
```

## run with 100GB urls
```
make run
```

# Algorithm
1. Split the input file into 1009 small files based on hash(url).
2. Load each small file, calculate the occurrences of urls by a dict, and then get the topn occurrences by a heap.
3. Merge all topn occurrences from step 2, and get final topn and print it.

# Complexity analysis
N is number of urls.
NS is number of split files, equal to 1009.
K is number of result urls we want, equal to 100.
BS is size of buffer size, maybe 4096 or 8192, see [disk io](#disk-io)

- step 1  
   time of read from input file or write to split file are both *N / BS * T(disk io)*,  
   time of hash calculation is *N * T(hash)*,  
   so the time complexity is *O(max(2 * N / BS * T(disk io), N * T(hash)))*.  
     
   only buffer is needed when read/write file,  
   so space complexity is *O(NS * BS)*.  
- step 2  
  time of read from split file is *N / NS / BS * T(disk io)*,  
  time of hash calculation is *N / NS * T(hash)*,  
  time of heap calculation is *N / NS * log(K)*,  
  and there are *NS* times,   
  so the time complexity is *O(max(N / BS * T(disk io), N * T(hash), N / NS * log(K)))*.  
    
  space complexity is *O(N / NS)*.  
- step 3  
  time complexity is *O(NS * K * log(K))*.  
     
  space complexity is *O(NS * K)*.

# Test Environment
1. 4 cores, 8GB memory
2. ubuntu 5.8.0-41-generic
3. hdd (105MB/s) with ext4

# Tests
## 1GB input file (~24s)
```
➜  topn git:(main) ✗ python topn.py urls.1G.txt
Calculate topn for urls.txt
140 http://gcmd.gsfc.nasa.gov/
...
80 http://www.pony.org/

time ellapsed: 24.51821141500841 seconds.
```

## 100GB input file (~5712s)
```
➜  topn git:(main) ✗ python topn.py urls.txt
Calculate topn for urls.txt
13034 http://gcmd.gsfc.nasa.gov/
...
7448 http://www.nlcnet.org/

time ellapsed: 5712.109350933999 seconds.
```

# Performance Profile (1GB)
In the [performance profile](./performance/scalene.txt), we can see the main bottlenecks is
1. disk IO
2. hash calculation

## disk IO
In python language, read/write for text file is bufferred by default, the buffer size is described by
[io.DEFAULT_BUFFER_SIZE](https://docs.python.org/3/library/io.html#io.DEFAULT_BUFFER_SIZE), typically
4096 or 8192. Other buffer sizes like 128KB is tested, but no improvement apparently.

## hash calculation
In python language, [hash](https://docs.python.org/3/library/functions.html#hash) function for bytes/string object is implement by [SipHash24](https://www.python.org/dev/peps/pep-0456/), which is fast and secure. I have tested time33 hash function in pure python or c module, all slow than builtin hash.

# Optimization (WIP)
## io_uring
For linux kernel version 5.1 or above, a new feature called io_uring is added. with a naive [test code](./wip/uring.c), about 30% improment over the normal read/write syscall.
```
➜  topn git:(main) ✗ echo 3 | sudo tee /proc/sys/vm/drop_caches
3
➜  topn git:(main) ✗ time cp urls.txt urls.cp.txt

real	0m50.677s
user	0m0.071s
sys 0m3.126s
➜  topn git:(main) ✗ echo 3 | sudo tee /proc/sys/vm/drop_caches
3
➜  topn git:(main) ✗ time ./uring urls.txt urls.uring.txt

real	0m35.226s
user	0m0.119s
sys	0m0.960s
```
## concurrent
Use multi-threads to do hash calculation, and sync with disk IO using a queue. But python has a poor multi-threads support, maybe fail.

## approximate algorithm
For some situation, approximate topn for large datasets is accetable. There are some algorithms like
1. [Efficient Computation of Frequent and Top-k Elements in Data Streams](http://www.cse.ust.hk/~raywong/comp5331/References/EfficientComputationOfFrequentAndTop-kElementsInDataStreams.pdf)
2. [Efficient Approximate Top-k Query Algorithm Using Cube Index](https://www.cs.yale.edu/homes/dongqu/APWeb11.pdf).

Systems like [Apache Druid](https://druid.apache.org/docs/latest/querying/topnquery.html), [Apache Kylin](http://kylin.apache.org/blog/2016/03/19/approximate-topn-measure/) all support approximate topn.

# Issues
## memory limit
In order to limit memory to 1GB when run tests, cgroup with memory.limit_in_bytes=1GB can be used.   
According to document [5.5 usage_in_bytes of cgroup](https://www.kernel.org/doc/Documentation/cgroup-v1/memory.txt), 
RSS+CACHE is calculated as usage bytes. so when open a file than 1GB size, usage_in_bytes will greater than limit_in_bytes, 
oom will triggerd.   
We may need write 1 to oom_control to disable oom killer. But if oom killer is disabled, when memory usage
is exceed, program will be suspend, we'll not be sure memory usage is below 1GB and also time measure is not accuracy.
