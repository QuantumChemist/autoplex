"""Flows to benchmark ML potentials."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from jobflow import Flow, Maker

if TYPE_CHECKING:
    from atomate2.common.schemas.phonons import PhononBSDOSDoc
    from pymatgen.core.structure import Structure

from autoplex.benchmark.phonons.jobs import compute_bandstructure_benchmark_metrics

__all__ = ["PhononBenchmarkMaker"]


@dataclass
class PhononBenchmarkMaker(Maker):
    """
    Maker to benchmark all chosen ML potentials on the DFT (VASP) reference data.

    Produces a phonon band structure comparison and q-point-wise phonons RMSE plots,
    as well as a summary text file.

    Parameters
    ----------
    name : str
        Name of the flow produced by this maker.
    """

    name: str = "PhononBenchmark"

    def make(
        self,
        ml_model: str,
        structure: Structure,
        benchmark_mp_id: str,
        ml_phonon_task_doc: PhononBSDOSDoc,
        dft_phonon_task_doc: PhononBSDOSDoc,
    ):
        """
        Make flow for benchmarking.

        Parameters
        ----------
        ml_model: str
            ML model to be used. Default is GAP.
        structure:
            Pymatgen structures drawn from the Materials Project.
        benchmark_mp_id: str.
            Materials project IDs for the structure.
        ml_phonon_task_doc: PhononBSDOSDoc
            Phonon task doc from ML potential consisting of pymatgen band-structure object.
        dft_phonon_task_doc: PhononBSDOSDoc
            Phonon task doc from DFT runs consisting of pymatgen band-structure object.
        """
        jobs = []

        benchmark_job = compute_bandstructure_benchmark_metrics(
            ml_model=ml_model,
            ml_phonon_bs=ml_phonon_task_doc.phonon_bandstructure,
            dft_phonon_bs=dft_phonon_task_doc.phonon_bandstructure,
            dft_imag_modes=dft_phonon_task_doc.has_imaginary_modes,
            ml_imag_modes=ml_phonon_task_doc.has_imaginary_modes,
            structure=structure,
        )
        jobs.append(benchmark_job)

        # create a flow including all jobs
        return Flow(jobs=jobs, output=benchmark_job.output, name=self.name)