---
id: cyas91wgnon0drwoacpverl
title: Root
desc: ''
updated: 1654046315352
created: 1653953339607
---

## Bio Information

I am a software engineer with over 30 years' experience in the industry. I have
presented papers on Software Configuration Management, Web Application
Development, and written for O'Reilly and Associates and other publishers. My
career has focused mainly on software automation and web-related applications.
My areas of personal interest include programming languages, compilers,
functional programming, and applications of large-scale numerical programming.
Past companies I have worked for include Red Hat Linux and NetApp, Inc. I am
currently with NVIDIA, where I develop the web portal for an IaaS team.

## Tasks and Tools Tracking

Here, I am keeping track of the tasks I've identified and the tools that I'm
using thus far. This is a precursor to shifting all or most of this to Dendron.

### Tasks

1. Gather references
2. Select example problem/exercise to implement
   1. C implementation
   2. Rust implementation
3. Gather comparative metrics
4. Write

### Tools

Tools I am currently using or expect to make use of:

* [VS Code](https://code.visualstudio.com/) - general editing
  * [Dendron](https://wiki.dendron.so/) - personal knowledge management (PKM)
  * Language modes for C and Rust
* [Org Mode](https://orgmode.org/index.html)
  * Emacs
  * [Plain Org](https://plainorg.com/) app
* [Rust](https://www.rust-lang.org/) - Rust language home page
* [rustup](https://rustup.rs/) - installer/manager for Rust
* [Valgrind](https://valgrind.org/) - memory profiling/dynamic analysis tool
* [TeXMaker](https://www.xm1math.net/texmaker/) TeX/LaTeX GUI editor

## Working Outline and Overview

### Overview

This is the overview (or "pitch"), which will eventually contribute to the
abstract:

> I would like to take the Rust programming language and see how well it
> performs in scientific programming applications. Rust has advantages over
> languages like C in memory handling and memory safety that I believe will
> make it an excellent candidate.
>
> Rust approaches the performance of C without the memory-related errors
> (memory allocation, pointer errors, etc.) which cause most of the critical
> bugs within C applications. Rust's promise of memory safety is what drew me
> to it.

### Outline

This is the basic outline as planned when the focus was more on numerical
computing. It needs to be revised and adjusted.

1. Introduction
   1. The State of High-Performance Computing
2. Background
   1. Introduction of Rust
   2. Interesting and Applicable Rust Features
3. Previous Research
4. Evaluation
   1. Performance Debugging of Rust
   2. Parallel Applications in Rust
   3. Interfacing to C Code
   4. Manually Optimizing Rust
5. Measuring and Comparing Performance
6. Results
7. Conclusion

### Approach

I would like to take a problem and implement it in both C and Rust, then
measure the comparative performance, their metrics (code size, binary size,
compilation time, etc.), with a focus on the memory issues. For instance, the
`valgrind` tool for C can identify memory issues, which can be compared to
Rust's identification of issues during compilation.

Some drawbacks:

* Due to my experience level, I won't be able to realistically compare development time between Rust and C.
* Rust does not currently have support for either OpenMP or MPI.
* I would like to eventually implement the code using CUDA as well, but Rust CUDA support is still very early-alpha.

## Draft of References

References will be gathered here, generally in plain text. Those that actually
become part of the bibliography will be moved to a BibTex file.

### References Already Evaluated

These are references that have been read and evaluated at this point. This does
not mean they will appear in the final set of references.

#### Books

"High Performance Compilers for Parallel Computing," Michael Wolfe.
Addison-Wesley Publishing, 1996. ISBN 0-8053-2730-4.

#### Papers

Ritke, Karl, "Using Rust as a Complement to C for Embedded Systems Software
Development." 2018.
<https://lup.lub.lu.se/student-papers/search/publication/8938297>

```BibTex
@misc{8938297,
  author       = {{Rikte, Karl}},
  issn         = {{1650-2884}},
  language     = {{eng}},
  note         = {{Student Paper}},
  series       = {{LU-CS-EX 2018-25}},
  title        = {{Using Rust as a Complement to C for Embedded Systems Software Development}},
  year         = {{2018}},
}
```

M. Costanzo, E. Rucci, M. Naiouf and A. D. Giusti, "Performance vs Programming
Effort between Rust and C on Multicore Architectures: Case Study in N-Body,"
2021 XLVII Latin American Computing Conference (CLEI), 2021, pp. 1-10, doi:
10.1109/CLEI53233.2021.9640225.

```BibTex
@INPROCEEDINGS{9640225,
  author={Costanzo, Manuel and Rucci, Enzo and Naiouf, Marcelo and Giusti, Armando De},
  booktitle={2021 XLVII Latin American Computing Conference (CLEI)},
  title={Performance vs Programming Effort between Rust and C on Multicore Architectures: Case Study in N-Body},
  year={2021},
  volume={},
  number={},
  pages={1-10},
  doi={10.1109/CLEI53233.2021.9640225}
}
```

Färnstrand, Linus, "Parallelization in Rust with fork-join and friends:
Creating the fork-join framework".
<https://odr.chalmers.se/handle/20.500.12380/219016?mode=full>

Sudwoj, Michal, "Rust programming language in the high-performance computing
environment".
<https://www.research-collection.ethz.ch/handle/20.500.11850/474922>

#### Web sites/articles

Comparing parallel Rust and C++:
<https://parallel-rust-cpp.github.io/introduction.html>

### References to be Evaluated

References that have not yet been read or vetted.

#### Papers Not Yet Read

---

### rj - I got these ideas from Sridhar

Programming languages ranked by expressiveness
<https://redmonk.com/dberkholz/2013/03/25/programming-languages-ranked-by-expressiveness/>

On the Expressive Power of Programming Languages
<https://jgbm.github.io/eecs762f19/papers/felleisen.pdf>

---

Multipattern string matching with q-grams
<https://dl.acm.org/doi/10.1145/1187436.1187438>

Real-Time Streaming String-Matching
<https://dl.acm.org/doi/10.1145/2635814>

GPU-accelerated string matching for database applications
<https://dl.acm.org/doi/10.1007/s00778-015-0409-y>

Disease Diagnosis Using Pattern Matching Algorithm from DNA Sequencing: a Sequential and GPGPU based Approach
<https://dl.acm.org/doi/10.1145/2980258.2980392>

Exhaustive exact string matching: the analysis of the full human genome
<https://dl.acm.org/doi/10.1145/3341161.3343517>

A constant-time optimal parallel string-matching algorithm
<https://dl.acm.org/doi/10.1145/129712.129720>

Parallel Approaches to the String Matching Problem on the GPU
<https://dl.acm.org/doi/10.1145/2935764.2935800>

A fast bit-parallel multi-patterns string matching algorithm for biological sequences
<https://dl.acm.org/doi/10.1145/1722024.1722077>

Efficient GPU Acceleration for Computing Maximal Exact Matches in Long DNA Reads
<https://dl.acm.org/doi/10.1145/3386052.3386066>

Analyzing DNA Strings using Information Theory Concepts
<https://dl.acm.org/doi/10.1145/2905055.2905074>

Efficient representation of DNA data for pattern recognition using failure factor oracles
<https://dl.acm.org/doi/10.1145/2513456.2513488>

Discovery of Regular Domains in Large DNA Data Sets
<https://dl.acm.org/doi/10.1145/3107411.3110419>

Approximate string matching in DNA sequences
<https://ieeexplore.ieee.org/abstract/document/1192395>

Importance of String Matching in Real World Problems
<https://www.researchgate.net/profile/Dr-Amit-Sinhal/publication/304305210_Importance_of_String_Matching_in_Real_World_Problems/links/576bb2f708aef2a864d3b881/Importance-of-String-Matching-in-Real-World-Problems.pdf>

Online Approximate String Matching with CUDA
<http://pds13.egloos.com/pds/200907/26/57/pattmatch-report.pdf>

Various String Matching Algorithms for DNA Sequences to Detect Breast Cancer using CUDA Processors
<http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.659.1224&rep=rep1&type=pdf>

GenASM: A High-Performance, Low-Power Approximate String Matching Acceleration Framework for Genome Sequence Analysis
<https://ieeexplore.ieee.org/abstract/document/9251930>

Exact Multiple Pattern Matching Algorithm using DNA Sequence and Pattern Pair
<http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.206.4954&rep=rep1&type=pdf>

A Composite Boyer-Moore Algorithm for the String Matching Problem
<https://ieeexplore.ieee.org/abstract/document/5704476>

On the massive string matching problem
<https://ieeexplore.ieee.org/abstract/document/7603199>

#### Papers Behind Paywalls

The WM-q multiple exact string matching algorithm for DNA sequences
<https://www.sciencedirect.com/science/article/abs/pii/S0010482521004509>

Fast string matching for DNA sequences
<https://www.sciencedirect.com/science/article/abs/pii/S0304397519305821>

Comparison of Exact String Matching Algorithms for Biological Sequences
<https://link.springer.com/chapter/10.1007/978-3-540-70600-7_31>

Fast string matching using an n-gram algorithm
<https://onlinelibrary.wiley.com/doi/abs/10.1002/spe.4380240105>

## Lookup

This section contains useful links to related resources.

* [Getting Started Guide](https://link.dendron.so/6b25)
* [Discord](https://link.dendron.so/6b23)
* [Home Page](https://wiki.dendron.so/)
* [Github](https://link.dendron.so/6b24)
* [Developer Docs](https://docs.dendron.so/)
