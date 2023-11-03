#!/bin/bash

echo
echo "🚀 Clean started at: $(date +'%Y-%m-%d %H:%M:%S')"
echo

p4a clean_dists
p4a clean_builds
p4a delete_dist

echo
echo "✅ Clean finished at: $(date +'%Y-%m-%d %H:%M:%S')"
echo

# p4a help:
#    clean_all (clean-all)
#                        Delete all builds, dists and caches
#    clean_dists (clean-dists)
#                        Delete all dists
#    clean_bootstrap_builds (clean-bootstrap-builds)
#                        Delete all bootstrap builds
#    clean_builds (clean-builds)
#                        Delete all builds
#    clean               Delete build components.
#                        .
#    clean_recipe_build (clean-recipe-build)
#                        Delete the build components of the given recipe. By default this will also delete built dists
#    clean_download_cache (clean-download-cache)
#                        Delete cached downloads for requirement builds
#    delete_dist (delete-dist)
#                        Delete a compiled dist

# p4a clean --help
#   positional arguments:
#    component           The build component(s) to delete. You can pass any number of arguments from
#                        "all", "builds", "dists", "distributions", "bootstrap_builds", "downloads"
