# Available Software

## Overview

Software on Juno is managed through the [module system](modules.md). Use `module avail` to browse everything installed, or `module avail <name>` to search for a specific package.

```bash
module avail             # list all available software
module avail python      # search by name
module load python/3.12.2
```

The tables below list software currently installed on Juno, grouped by category. The **Module** column shows the command to load each package. Versions marked **(D)** are the default loaded when no version is specified.

---

## Compilers

| Software | Version(s) | Module | Description |
|---|---|---|---|
| GNU Compiler Collection | 5.5, 8.5, 9.3, 11.3, 12.4, 13.2, **14.2 (D)** | `module load gnu14` | C, C++, and Fortran compilers (`gcc`, `g++`, `gfortran`) |
| Intel oneAPI | 2023.2, **2025.0 (D)** | `module load intel/2025.0` | Intel C, C++, and Fortran compilers, optimized for Intel hardware |
| AOCC | 5.0 | `module load aocc/5.0` | AMD Optimizing C/C++ Compiler |
| NVHPC | 24.11 | `module load nvhpc/24.11` | NVIDIA HPC SDK — C, C++, and Fortran with GPU directives (OpenACC, OpenMP offload) |

---

## Programming Languages

| Software | Version(s) | Module | Description |
|---|---|---|---|
| Python | 3.11.11, **3.12.2 (D)** | `module load python/3.12.2` | General-purpose scripting and scientific computing |
| R | 4.5.0 | `module load R/4.5.0` | Statistical computing and graphics |
| Julia | 1.11.3 | `module load julia/1.11.3` | High-performance numerical computing |
| MATLAB | r2024b | `module load matlab/r2024b` | Mathematical computing environment (licensed) |
| Java | 11 | `module load java/11` | Java Development Kit (JDK) |
| Lua | 5.4.7 | `module load lua/5.4.7` | Lightweight scripting language |
| Stata | 19.5 | `module load stata/19.5` | Statistical analysis (licensed) |

---

## MPI & Parallel Communication

| Software | Version(s) | Module | Description |
|---|---|---|---|
| OpenMPI | 4.1.6, **5.0.7 (D)** | `module load openmpi5` | Open-source MPI implementation (default on Juno) |
| MPICH | 3.4.3-ofi, **3.4.3-ucx (D)** | `module load mpich` | Portable MPI reference implementation |
| OpenMPI (AOCC) | 5.0.6 | `module load openmpi-aocc/5.0.6` | OpenMPI built with the AMD AOCC compiler |
| OpenCoarrays | 2.10.2 | `module load opencoarrays/2.10.2` | Fortran coarray parallelism library |

---

## GPU Computing

| Software | Version(s) | Module | Description |
|---|---|---|---|
| CUDA | 11.7, 12.4, 12.6, **13.0 (D)** | `module load cuda/12.6` | NVIDIA GPU programming toolkit |
| CUDA-Q | 0.12.0 | `module load cuda-q/0.12.0` | Hybrid quantum-classical computing on GPU |
| NCCL | 2.29.2 (cuda12.4) | `module load nccl/2.29.2-1-cuda12.4` | NVIDIA collective communications library for multi-GPU |
| NVSHMEM | 3.5.19 (cuda12.4) | `module load nvshmem/3.5.19-cuda12.4` | OpenSHMEM-based GPU memory library |
| Ollama | 12, 15, **21 (D)** | `module load ollama/21` | Run large language models locally on GPU |

---

## Computational Chemistry & Molecular Dynamics

| Software | Version(s) | Module | Description |
|---|---|---|---|
| Gaussian | 16 | `module load gaussian/16` | Quantum chemistry (licensed) |
| ORCA | 6.0.1, **6.1.1 (D)** | `module load orca/6.1.1` | Quantum chemistry — DFT, coupled cluster, and more |
| Q-Chem | 6.2.2, **6.3 (D)** | `module load qchem/6.3` | Quantum chemistry (licensed) |
| Quantum ESPRESSO | 7.3.1 | `module load qe/7.3.1` | Plane-wave DFT for electronic structure |
| CASTEP | 25.12 | `module load castep/25.12` | Plane-wave DFT materials modeling (licensed) |
| SIESTA | 5.2.1-parallel, **5.4.2-wannier90 (D)** | `module load siesta/5.4.2-wannier90` | DFT for large systems with Wannier90 |
| VASP | 6.4.2-upgrade, **6.4.2-wannier90-only (D)** | `module load vasp/6.4.2-wannier90-only` | DFT electronic structure (licensed) |
| GROMACS | 2024.5-plumed | `module load gromacs/2024.5-plumed` | Molecular dynamics with PLUMED enhanced sampling |
| AMBER | 24-beta, **24 (D)** | `module load amber/24` | Molecular dynamics (licensed) |
| NAMD | 3.0.1 | `module load namd/3.0.1` | Scalable molecular dynamics |
| TINKER | 9 | `module load tinker/9` | Molecular mechanics and dynamics |
| AutoDock Vina | 1.2.7 | `module load autodock_vina/1.2.7` | Molecular docking |
| Rosetta | 3.15 | `module load rosetta/3.15` | Protein structure prediction and design |
| LICHEM | lichem | `module load lichem/lichem` | QM/MM calculations |
| BCL | 4.3.1 | `module load bcl/4.3.1` | Biochemistry library — cheminformatics |
| DiagHam | 0.01 | `module load diagham/0.01` | Exact diagonalization for quantum many-body systems |

---

## Engineering & Simulation

| Software | Version(s) | Module | Description |
|---|---|---|---|
| ANSYS | **2025R1** (also 2024R2) | `module load ansys/2025R1` | Simulation suite: Fluent, Workbench, Mechanical, AnsysEM, Autodyn (licensed) |
| Abaqus | 2023, **2026 (D)** | `module load abaqus/2026` | Finite element analysis (licensed) |
| COMSOL | 6.4 | `module load comsol/6.4` | Multiphysics simulation (licensed) |
| OpenFOAM | 2512 | `module load openfoam/2512` | Computational fluid dynamics |
| FVCOM | 5.0.1 | `module load fvcom/5.0.1` | Finite-volume coastal ocean model |
| NonLinLoc | 7.1.04 | `module load nonlinloc/7.1.04` | Probabilistic earthquake location |

---

## Optimization & Mathematical Programming

| Software | Version(s) | Module | Description |
|---|---|---|---|
| CPLEX | 22.1.2 | `module load cplex/22.1.2` | Mixed-integer programming solver (licensed) |
| Gurobi | 12.0.1 | `module load gurobi/12.0.1` | Mathematical optimization solver (licensed) |

---

## Bioinformatics & Neuroimaging

| Software | Version(s) | Module | Description |
|---|---|---|---|
| AFNI | 25.3.03 | `module load afni/25.3.03` | Neuroimaging analysis suite |
| FSL | 6.0.7.19 | `module load fsl/6.0.7.19` | FMRIB Software Library for neuroimaging |

---

## EDA & Semiconductor

| Software | Version(s) | Module | Description |
|---|---|---|---|
| CyberWorkbench | 10.1.7 | `module load cyberworkbench/10.1.7` | High-level synthesis and verification (licensed) |
| TCAD Silvaco | 243422 | `module load tcad-silvaco/243422` | Semiconductor device and process simulation (licensed) |

---

## Numerical Libraries

| Software | Version(s) | Module | Description |
|---|---|---|---|
| OpenBLAS | 0.3.29 | `module load openblas/0.3.29` | Optimized BLAS and LAPACK routines |
| FFTW | 3.3.10 | `module load fftw/3.3.10` | Fast Fourier transforms |
| ScaLAPACK | 2.2.2 | `module load scalapack/2.2.2` | Distributed-memory linear algebra |
| PLASMA | 24.8.7 | `module load plasma/24.8.7` | Parallel linear algebra for multicore |
| PETSc | 3.18.1 | `module load petsc/3.18.1` | Scalable solvers for PDEs |
| HYPRE | 2.33.0 | `module load hypre/2.33.0` | Parallel multigrid and Krylov solvers |
| Trilinos | 13.4.0 | `module load trilinos/13.4.0` | Sandia's suite of scientific algorithms |
| MUMPS | 5.2.1 | `module load mumps/5.2.1` | Parallel sparse direct solver |
| SuperLU | 7.0.0 | `module load superlu/7.0.0` | Sparse LU factorization |
| SuperLU_DIST | 6.4.0 | `module load superlu_dist/6.4.0` | Distributed-memory sparse direct solver |
| SLEPc | 3.18.0 | `module load slepc/3.18.0` | Parallel eigenvalue solver (builds on PETSc) |
| GSL | 2.8 | `module load gsl/2.8` | GNU Scientific Library |
| Boost | 1.88.0 | `module load boost/1.88.0` | C++ general-purpose libraries |
| MFEM | 4.4 | `module load mfem/4.4` | Scalable finite element library |
| METIS | 5.1.0 | `module load metis/5.1.0` | Graph/mesh partitioning |
| Scotch / PT-Scotch | 7.0.7 | `module load scotch/7.0.7` | Graph partitioning and sparse matrix ordering |

---

## Data Formats & I/O

| Software | Version(s) | Module | Description |
|---|---|---|---|
| HDF5 | **1.14.6 (D)**, 1.13.2-nvhpc | `module load hdf5/1.14.6` | Hierarchical data format |
| NetCDF | 4.9.3 | `module load netcdf/4.9.3` | Network common data form (C interface) |
| NetCDF-Fortran | **4.6.2 (D)**, 4.6.1-nvhpc | `module load netcdf-fortran/4.6.2` | NetCDF Fortran interface |
| NetCDF-C++ | 4.3.1 | `module load netcdf-cxx/4.3.1` | NetCDF C++ interface |
| PnetCDF | 1.14.0 | `module load pnetcdf/1.14.0` | Parallel NetCDF for MPI applications |
| Parallel HDF5 | 1.14.6 | `module load phdf5/1.14.6` | HDF5 with MPI-IO support |
| ADIOS2 | 2.10.1 | `module load adios2/2.10.1` | Adaptable I/O system for large-scale simulations |
| SIONlib | 1.7.7 | `module load sionlib/1.7.7` | Scalable parallel I/O for task-local files |

---

## Profiling & Performance Analysis

| Software | Version(s) | Module | Description |
|---|---|---|---|
| TAU | 2.31.1 | `module load tau/2.31.1` | Tuning and analysis utilities — MPI, OpenMP, CUDA profiling |
| Score-P | 9.0 | `module load scorep/9.0` | Scalable performance measurement infrastructure |
| Scalasca | 2.6.2 | `module load scalasca/2.6.2` | Scalable MPI/OpenMP performance analysis |
| Extrae | 3.8.3 | `module load extrae/3.8.3` | Instrumentation framework for parallel programs |
| Dimemas | 5.4.2 | `module load dimemas/5.4.2` | MPI performance simulator |
| OTF2 | 3.1.1 | `module load otf2/3.1.1` | Open trace format library |
| PAPI | 6.0.0 | `module load papi/6.0.0` | Hardware performance counter API |
| Likwid | 5.4.1 | `module load likwid/5.4.1` | Performance monitoring and benchmarking tools |
| AMD uProf | 5.1.7 | `module load amduprof/5.1.7` | AMD CPU/GPU profiling |
| Valgrind | 3.24.0 | `module load valgrind/3.24.0` | Memory error detection and profiling |
| Gotcha | 1.0.8 | `module load gotcha/1.0.8` | Function wrapping / interposition library |
| CubeLib / CubeW | 4.9 | `module load cubelib/4.9` | Cube performance report format and writer |
| Opari2 | 2.0.9 | `module load opari2/2.0.9` | OpenMP source-code instrumentor |
| PDToolkit | 3.25.1 | `module load pdtoolkit/3.25.1` | Program database toolkit |
| HPCC | 1.5 | `module load hpcc/1.5` | HPC Challenge benchmark suite |
| IMB | 2021.3 | `module load imb/2021.3` | Intel MPI benchmarks |
| OMB | 7.5 | `module load omb/7.5` | OSU micro-benchmarks for MPI latency/bandwidth |

---

## Containers

| Software | Version(s) | Module | Description |
|---|---|---|---|
| Apptainer | 1.3.4 | `module load apptainer/1.3.4` | Container runtime (successor to Singularity) — run Docker images on HPC |
| Charliecloud | 0.15 | `module load charliecloud/0.15` | Rootless container runtime |

See the [Containers Guide](../advanced/containers.md) for usage details.

---

## Development & Build Tools

| Software | Version(s) | Module | Description |
|---|---|---|---|
| CMake | 4.0.0 | `module load cmake/4.0.0` | Cross-platform build system generator |
| EasyBuild | 5.0.0 | `module load EasyBuild/5.0.0` | HPC software build and installation framework |
| Spack | 0.23.1 | `module load spack/0.23.1` | Package manager for HPC software |
| Miniconda | 24.11.1 | `module load miniconda/24.11.1` | Conda package and environment manager |
| Code-Server | 3.10.2, 4.100.2, **4.108.2 (D)** | `module load code-server/4.108.2` | VS Code in the browser |
| GNUplot | 6.0.4 | `module load gnuplot/6.0.4` | Command-line plotting |
| jq | 1.7.1 | `module load jq/1.7.1` | Lightweight JSON processor |
| Launcher | 3.9 | `module load launcher/3.9` | Parametric job launcher for task arrays |
| KempnerPulse | 0.4.1 | `module load kempnerpulse/0.4.1` | AI workload management tools |

---

## Requesting New Software

If software you need is not listed here:

1. **Try a user-space install first** — Python packages (`pip install --user`), R packages (`install.packages()`), or Conda environments often don't require admin access. See [Miniconda](../advanced/miniconda.md).

2. **Use a container** — If the software has a Docker or Apptainer image, you can often run it directly. See [Containers](../advanced/containers.md).

3. **Open a support ticket** — Email [circ-assist@utdallas.edu](mailto:circ-assist@utdallas.edu) and include:
    - Software name, version, and official URL
    - Brief description of your use case
    - License type (open source or commercial)
    - Whether other users would benefit

---

## Related Pages

- [Module System](modules.md) — how to load, search, and manage modules
- [Common Scientific Programs](../running-programs/common-programs.md) — job script examples for popular software
- [Miniconda](../advanced/miniconda.md) — Python environment management
- [Containers](../advanced/containers.md) — running containerized software
