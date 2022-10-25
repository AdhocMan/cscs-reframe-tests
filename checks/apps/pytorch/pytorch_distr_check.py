import os
import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class pytorch_distr_cnn(rfm.RunOnlyRegressionTest):
    descr = 'Check the training throughput of a cnn with torch.distributed'
    platform = parameter(['native', 'Sarus', 'Singularity'])
    valid_systems = ['hohgant:gpu']
    valid_prog_environs = ['builtin']
    sourcesdir = 'src'
    num_tasks = 16
    num_tasks_per_node = 4
    num_gpus_per_node = 4
    throughput_per_gpu = 864.62
    executable = 'python cnn_distr.py'
    throughput_total = throughput_per_gpu * num_tasks
    reference = {
        'hohgant:gpu': {
            'samples_per_sec_per_gpu': (throughput_per_gpu,
                                        -0.1, None, 'samples/sec'),
            'samples_per_sec_total': (throughput_total,
                                      -0.1, None, 'samples/sec')
        }
    }

    @run_after('init')
    def skip_native_test(self):
        # FIXME: Remove when PyTorch is available on Hohgant
        self.skip_if(self.platform == 'native')

    @run_before('run')
    def set_container_variables(self):
        container_platform = (
            self.platform if self.platform != 'native' else None
        )
        self.container_platform.image = 'nvcr.io/nvidia/pytorch:22.08-py3'
        self.container_platform.command = self.executable
        self.container_platform.with_cuda = True

    @sanity_function
    def assert_job_is_complete(self):
        return sn.assert_found(r'Total average', self.stdout)

    @performance_function('samples/sec')
    def samples_per_sec_per_gpu(self):
        return sn.avg(sn.extractall(
            r'Epoch\s+\d+\:\s+(?P<samples_per_sec_per_gpu>\S+)\s+images',
            self.stdout, 'samples_per_sec_per_gpu', float
        ))

    @performance_function('samples/sec')
    def samples_per_sec_total(self):
        return sn.avg(sn.extractall(
            r'Total average: (?P<samples_per_sec_total>\S+)\s+images',
            self.stdout, 'samples_per_sec_total', float
        ))

    @run_before('run')
    def set_visible_devices_per_rank(self):
        self.job.launcher.options = ['./set_visible_devices.sh']
        if self.platform != 'native':
            self.job.launcher.options = (
                ['--mpi=pmi2'] + self.job.launcher.options
            )
