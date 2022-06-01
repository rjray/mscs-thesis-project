---
id: cyas91wgnon0drwoacpverl
title: Root
desc: ''
updated: 1654046954137
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

## Lookup

This section contains useful links to related resources.

* [Getting Started Guide](https://link.dendron.so/6b25)
* [Discord](https://link.dendron.so/6b23)
* [Home Page](https://wiki.dendron.so/)
* [Github](https://link.dendron.so/6b24)
* [Developer Docs](https://docs.dendron.so/)
