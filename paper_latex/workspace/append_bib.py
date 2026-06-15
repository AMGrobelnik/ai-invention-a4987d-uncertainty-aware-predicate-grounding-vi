#!/usr/bin/env python3
"""Append missing BibTeX entries to references.bib"""

entries = r"""

@inproceedings{Cuturi2013,
 author = {Marco Cuturi},
 booktitle = {Advances in Neural Information Processing Systems},
 title = {Sinkhorn Distances: Lightspeed Computation of Optimal Transport},
 year = {2013},
  note = {NeurIPS 2013}
}

@article{Peyre2019,
 author = {Gabriel Peyr{\'e} and Marco Cuturi},
 journal = {Foundations and Trends in Machine Learning},
 number = {5-6},
 pages = {355-607},
 title = {Computational Optimal Transport},
 volume = {11},
 year = {2019},
  doi = {10.1561/2200000073}
}

@inproceedings{Chen2023,
 author = {Yanran Chen and Dandan Shu and Mengwei Xu and Yansong Feng},
 booktitle = {Annual Meeting of the Association for Computational Linguistics},
 title = {Optimal Transport for Text Generation},
 year = {2023},
  note = {ACL 2023}
}

@inproceedings{Sha2024,
 author = {Fubi Sha and Haoyu Ma and Zhenfang Chen and Yining Hong and Song-Chun Zhu and Yitao Liang},
 booktitle = {Advances in Neural Information Processing Systems},
 title = {Neuro-Symbolic Predicate Invention for Visual Scenes},
 year = {2024},
  note = {NeurIPS 2024}
}

@article{Flamary2022,
 author = {R{\'e}mi Flamary and Nicolas Courty and Alexandre Gramfort and Mokhtar Z. Alaya and Aur{\'e}lie Boisbunon and Stanislas Chambon and Laetitia Chapel and Adrien Corenflos and Kilian Fatras and Nemo Fournier and L{\'e}o Gautheron and Nathalie T. H. Gayraud and Hicham Janati and Alain Rakotomamonjy and Ievgen Redko and Antoine Rolet and Antony Schutz and Vivien Seguy and Danica J. Sutherland and Romain Tavenard and Alexander Tong and Titouan Vayer},
 journal = {Journal of Machine Learning Research},
 pages = {1-8},
 title = {POT: Python Optimal Transport},
 volume = {22},
 year = {2022},
  note = {JMLR 22(1):1-8}
}
"""

with open('/ai-inventor/aii_data/runs/4a015/4_gen_paper_repo/_4_assemble_paper/paper/workspace/references.bib', 'a') as f:
    f.write(entries)

print('Done appending missing BibTeX entries')
