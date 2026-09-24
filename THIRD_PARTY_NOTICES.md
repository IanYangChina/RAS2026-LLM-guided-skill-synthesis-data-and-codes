# Third-party notices

The MIT license in [`LICENSE`](LICENSE) covers the original Python runtime,
public scripts, and documentation in this repository. It does not replace the
licenses of bundled models, meshes, or external software.

## MuJoCo

The simulator is provided by the `mujoco` Python package and the MuJoCo
physics engine. MuJoCo is distributed by Google DeepMind under the Apache
License 2.0. Consult the installed package and the upstream project for the
complete license text and notices:

- <https://github.com/google-deepmind/mujoco>
- <https://www.apache.org/licenses/LICENSE-2.0>

## Franka Emika Panda model

The immediate bundled MJCF source is the
[DeepMind MuJoCo Menagerie `franka_emika_panda` model](https://github.com/google-deepmind/mujoco_menagerie/tree/main/franka_emika_panda).
The model's documented geometry and kinematic provenance follows the public
[Franka ROS `franka_description`](https://github.com/frankaemika/franka_ros/tree/develop/franka_description)
package. The local asset copy retains the upstream Apache-2.0 notice at
[`simulation/assets/robots/franka_emika_panda/LICENSE`](simulation/assets/robots/franka_emika_panda/LICENSE).

No upstream Menagerie commit, tag, or release identifier is embedded in the
bundled model files, so this archive does not assert an upstream revision. The
SHA-256 hashes of the actual files are the authoritative local provenance for
replay and redistribution checks. The robot model is a simulation description;
this archive does not grant any trademark or hardware rights.

## Other model and mesh assets

Task object XML files and any gripper or robot descriptions supplied with the
release retain the license files shipped alongside those assets. Do not remove
those notices when redistributing modified asset bundles. Review the
asset-specific README and LICENSE files before using a model outside this
archive.

## Python dependencies

Dependency licenses are available from the package metadata installed by
`environment.yml` and `pyproject.toml`. They remain the responsibility of the
respective projects. This archive does not bundle or modify their license
terms.
