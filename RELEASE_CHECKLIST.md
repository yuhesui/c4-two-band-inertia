# Release checklist

1. Run `python software/run_all.py`.
2. Run `python -m unittest discover -s tests -v`.
3. Run `cd lean`, `lake exe cache get`, and `lake build`.
4. Create a Zenodo draft and reserve its DOI before publication.
5. Add the reserved DOI to `CITATION.cff` and the manuscript's Code Availability statement.
6. Confirm that `CITATION.cff` and `.zenodo.json` describe the same title, authors, version, license, and keywords. Zenodo gives `.zenodo.json` precedence when both files exist.
7. Set the actual release date in `CITATION.cff`.
8. Regenerate `SHA256SUMS` after all metadata changes and verify every entry.
9. Commit and push the final package to the public GitHub repository.
10. Confirm that GitHub Actions passes on Python 3.12 and 3.13 and that the Lean build, Lean checker, and `nanoda` checker all pass.
11. Create the immutable `v1.0.0` tag and GitHub release from that exact commit.
12. Archive that exact release in the prepared Zenodo record and publish it.
13. Verify that the DOI resolves, the GitHub release matches the archive, and the archived checksums pass.

Do not modify an existing release tag. Publish later corrections under a new semantic version.
