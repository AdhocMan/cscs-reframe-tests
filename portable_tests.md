# How to make your tests more portable

## Features and extras in valid systems and programming environment

In order for tests to be as generic as possible we define the `valid_systems` and `valid_prog_environs` with features that should be defined in the configuration.
More information [in the documentation of ReFrame](https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#reframe.core.pipeline.RegressionTest.valid_systems).

Examples of usage:

```python
@rfm.simple_test
class GPUTest(rfm.RegressionTest):
    # Test that will test all the remote partitions (compute nodes) that
    # have an NVIDIA GPU
    valid_systems = ['+nvgpu +remote']
    valid_prog_environs = ['+cuda']
    ...

@rfm.simple_test
class LoginNodesTest(rfm.RegressionTest):
    # Test that will run on the login nodes
    valid_systems = ['-remote']
    ...
```

### Features for partitions

| Feature | Description | Notes |
| --- | --- | --- |
| gpu | The partitions has a GPU | |
| nvgpu | The partitions has an NVIDIA GPU | Typically used with an environment with the `cuda` feature |
| amdgpu | The partitions has an AMD GPU | | |
| remote | The partitions has a remote scheduler (set when you want to test the compute nodes of a cluster) | | |
| login | This partition includes login nodes | | |
| sarus | Sarus is available in this partition | | |
| singularity | Singularity is available in this partition | | |
| uenv | Supports mounting and using user environments | |

### Features for environments

| Feature | Description | Notes |
| --- | --- | --- |
| cpe | This a CRAY based environment | |
| cuda | The environment has a CUDA compiler | |
| compiler | The environment provides a typical compiler | |
| openmp | The compiler of the environment supports openmp |
| mpi | The compiler of the environment supports openmp | |
| gromacs | GROMACS is available in this environment | |
| netcdf-hdf5parallel | | |
| pnetcdf | | |
| alloc_speed | | |
| cuda-fortran | | |
| openacc | | |
| opencl | | |

## How to use the value of `extras` in a test

In the configuration of ReFrame, the user can define their own `extras` property in each [partition](https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#reframe.core.systems.SystemPartition.extras) and [environment](https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#reframe.core.environments.Environment.extras).
The values of these fields are simply objects of type `Dict[str, object]` and they are available in a test after the `setup` phase.

Here is an example how to use these features in a tests:

```python
    @run_after('setup')
    def set_memory(self):
        max_memory = self.current_partition.extras['cn_memory']
        ...

    @run_after('setup')
    def set_compilation_flags(self):
        self.build_system.cflags = self.current_environ.extras['openmp_flags'] + ['-O3']
        ...
```

### Extras for partitions

| Extras | Description | Type | Example value |
| --- | --- | --- | --- |
| cn_memory | Compute node memory | integer | 500 |
| launcher_options | | list[string] | ['--mpi=pmi2']

### Extras for environments

| Extras | Description | Type | Example value |
| --- | --- | --- | --- |
| openmp_flags | | list[string] | [' -fopenmp'] |
| launcher_options | | list[string] | ['--mpi=pmi2']

## How to use the processor/device specs in a test

Another way to keep your tests as generic as possible is to use the processor information that is collected during the [auto-detection](https://reframe-hpc.readthedocs.io/en/stable/configure.html#auto-detecting-processor-information).
You can find an overview of the available processor information [here](https://reframe-hpc.readthedocs.io/en/stable/config_reference.html#processor-info).

Here is an example from a test:

```python
class MemBandwidthTest(rfm.RunOnlyRegressionTest):
    ...
    @run_before('run')
    def set_processor_properties(self):
        # This is a function that is provided by ReFrame so that the test
        # is automatically skipped when the processor information is not
        # available
        self.skip_if_no_procinfo()

        # The test will get the number of CPUs and numa nodes that Reframe
        # has detected for this partition
        processor_info = self.current_partition.processor
        self.num_cpus_per_task = processor_info.num_cpus
        numa_nodes = processor_info.topology['numa_nodes']

        self.numa_domains = [f'S{i}' for i, _ in enumerate(numa_nodes)]
        self.num_cpu_domain = (
            self.num_cpus_per_task // (len(self.numa_domains) *
                                       self.num_tasks_per_core)
        )
        ...
```

Currently, ReFrame supports auto-detection of the local or remote processor information only.
It does not support auto-detection of devices, in which cases users should explicitly specify this information using the `devices` [configuration option](https://reframe-hpc.readthedocs.io/en/stable/config_reference.html#config.systems.partitions.devices).

## How to test containers

## Continuous Integration

Testing of CPE and UENV software stacks is automated using CSCS CI. A list of the current ReFrame tests integrated in the CI can be found here:
- CPE: https://gitlab.com/cscs-ci/ci-testing/webhook-ci/mirrors/6557018579987861/835515875116200/-/pipelines
- UENV: https://gitlab.com/cscs-ci/ci-testing/webhook-ci/mirrors/551234120955960/1440398897047549/-/pipelines