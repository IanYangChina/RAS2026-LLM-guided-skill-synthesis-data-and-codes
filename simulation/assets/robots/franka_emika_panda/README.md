# Franka Emika Panda MJCF

This bundled robot description follows the
[DeepMind MuJoCo Menagerie `franka_emika_panda` model](https://github.com/google-deepmind/mujoco_menagerie/tree/main/franka_emika_panda).
The geometry and kinematic source chain is documented by the public
[Franka ROS `franka_description`](https://github.com/frankaemika/franka_ros/tree/develop/franka_description)
package. The local model files are the copy used by the simulation scenes in
this archive.

The asset directory contains the Panda arm, no-hand and hand variants, task
attachments, meshes, and scene include files. The archive does not include an
upstream Menagerie commit or tag in the asset metadata; use the SHA-256 values
recorded by the public catalog for exact local-file identity.

The model is released under the Apache-2.0 terms in [`LICENSE`](LICENSE).
Those terms apply to this model and do not grant any trademark or hardware
rights. The archive's own runtime code is licensed separately under the root
MIT license.
