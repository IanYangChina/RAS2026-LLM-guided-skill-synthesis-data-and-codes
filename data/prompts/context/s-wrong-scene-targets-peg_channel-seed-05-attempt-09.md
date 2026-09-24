## Search State

- **Seed**: 5
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | force_exceeded | 5 | 0.3715 | 0.20 | ❌ rejected |
| 8 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | time_limit | force_exceeded | 6 | 0.8124 | 0.00 | ❌ rejected |
| 7 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 5 | 0.0958 | 0.37 | ✅ accepted |
| 6 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | force_exceeded | 6 | -0.1409 | 0.00 | ❌ rejected |
| 5 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 5 | -0.0721 | 0.12 | ✅ accepted |

**Proposal policy**: task_score is 0.20 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: peg_channel
- Frozen realised-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`
- Frozen object start: [0.5244002338996304, -0.05536473682108051, 0.04]
- Frozen task target: [0.5, 0.2, 0.3]
- Goal object position: (0.5, 0.2, 0.3)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5244002338996304, -0.05536473682108051, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5244002338996304, 0.1046352631789195, 0.04)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5244002338996304, 0.1046352631789195, 0.04]
objects:
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    radius_m: 0.018
    half_length_m: 0.025
  - name: channel_structure
    role: fixture
    dynamics: static
    geometry: two_parallel_walls
    inner_gap_m: 0.05
    wall_thickness_m: 0.03
    wall_height_m: 0.05
task_landmarks:
  frozen_object_start: [0.5244, 0.1046, 0.04]
  frozen_task_target: [0.5244, -0.0554, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5244002338996304, -0.05536473682108051, 0.04]}
  frozen_targets: {'channel_exit': [0.5, 0.2, 0.3]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.5244002338996304, -0.05536473682108051, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.2, 0.3) | final destination targets |
| `fixture` | offset from fixture pose (0.54, 0.0, 0.035) | approach/contact targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.371) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_contact
  anchor: object
  offset:
  - 0.0
  - 0.02
  - 0.04
  weight: 0.3
- id: push_through_channel
  anchor: object
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_contact
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - -0.024
    - 0.02
    - 0.0
    tolerance: 0.005
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.002
      - 0.02
      default: 0.005
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: contact_approach
    when: during_phase
    predicate: contact_detected
    threshold: 0.0
    on_failure: continue
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_contact
- id: push_along_channel
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - -0.024
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.03
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: contact_during_push
    when: during_phase
    predicate: contact_detected
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.0
    - 0.0
  subtask_id: push_through_channel

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_contact** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[-0.024, 0.02, 0.0], tolerance=0.005
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=contact_approach, when=during_phase, predicate=contact_detected, on_failure=continue, threshold=0.0
  - retries: max_attempts=0, strategy=repeat
- **push_along_channel** (`push`)
  - target: source=yaml, anchor=task_object, offset=[-0.024, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.03
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=contact_during_push, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.371
- **task_score** (E): 0.201
- **fitness_score**: 0.288  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.250

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 0.67 | 0.67 | 0.1752 |
| push_along_channel | 0.67 | 0.67 | 0.0471 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 0.67 / step_budget | (0.500, 0.200, 0.300)→(0.509, 0.156, 0.131) | (0.512, 0.095, 0.040)→(0.504, 0.089, 0.038) | 0.175→0.169 | 0.67 / 1.000 | 28.811 | 83.675 |
| push_along_channel | push | 0.67 / force_exceeded | (0.509, 0.156, 0.131)→(0.507, 0.109, 0.127) | (0.504, 0.089, 0.038)→(0.501, 0.043, 0.034) | 0.169→0.124 | 0.67 / 1.667 | 32.227 | 44.057 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.962
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.601
- phase_score: 0.790
- phase_breakdown.push_through_channel_score: 0.772
- phase_breakdown.reach_contact_score: 0.831

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.714
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.601
- **Median Q (composite search score)**: 0.399
- **K-run variance**: 0.2459
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.7
- **Final σ (mean)**: 0.285


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `9b36d26f861d7a613dfb3d8c86d70470e42095a430c2befa4bd6e530468a8a7e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `2af86d8f59685db6584febc0596b9044223ae39cea3120c112c665a54a1c4732`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,-0.05536,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,-0.05536,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90625,"average_solve_count":64.0,"average_success_count":64.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.09092,"approach_peg.approach_tolerance":0.0159,"push_along_channel.force_threshold":26.72922,"push_along_channel.push_distance":0.21159,"push_along_channel.push_speed":0.08334},"optimized_scores":{"best_composite_score":0.39933,"best_fitness_score":0.14933,"best_task_score":0.00047},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":65.0,"contact_point_centroid":[0.52538,0.11996,0.06],"force_p95":111.1031,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":130.12516,"mean_force":88.44709,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51995,0.13169,0.0511]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52712,0.11999,0.06],"force_p95":103.29816,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":105.07276,"mean_force":87.32677,"phase_index":1.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.52125,0.13211,0.04471]},{"body_a":"peg","body_b":"channel_base_body","contact_count":972.0,"contact_point_centroid":[0.5057,0.10462,0.00938],"force_p95":0.5771,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.16552,"mean_force":0.71423,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50949,0.16106,0.16315]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.51604,0.11919,0.05864],"force_p95":31.38479,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.64498,"mean_force":15.23537,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51849,0.13067,0.05761]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49969,0.19889,0.29688]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.51818,0.09785,0.00939],"force_p95":0.56545,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56719,"mean_force":0.55304,"phase_index":1.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.52126,0.13213,0.04471]}],"total_contact_groups":6},"final_pose_error":0.24003,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50577,0.10449,0.03382],"final_tcp_position":[0.52113,0.1321,0.04454],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":130.12516,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":999.0,"n_steps_budget":1000.0,"object_pos_end":[0.50573,0.1044,0.03383],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18459,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":86.22784,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1079.0,"raw_peak_contact_force":130.12516,"subtask_id":"reach_contact","tcp_end":[0.5213,0.13209,0.04481],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.03362,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.50577,0.10449,0.03382],"object_pos_start":[0.50573,0.1044,0.03383],"object_to_goal_dist_end":0.18468,"object_to_goal_dist_start":0.18459,"object_z_max":0.03383,"peak_contact_force":69.58077,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":105.07276,"subtask_id":"push_through_channel","tcp_end":[0.52113,0.1321,0.04454],"tcp_start":[0.5213,0.13209,0.04481],"tcp_to_object_dist_end":0.03336,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `314cefd2153cfe84bc0d0d2dfbeb7f4daf8feaf5f2c7ce7d396802b52a157f39`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,-0.09254,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,-0.09254,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":1.0,"average_solve_count":4.0,"average_success_count":4.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.12057,"approach_peg.approach_tolerance":0.01369,"push_along_channel.force_threshold":21.56525,"push_along_channel.push_distance":0.15756,"push_along_channel.push_speed":0.06334},"optimized_scores":{"best_composite_score":-0.24938,"best_fitness_score":0.00062,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.38936,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50305,0.06746,0.03961],"final_tcp_position":[0.49973,0.19959,0.30009],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.06746,0.03996],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14749,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_contact","tcp_end":[0.4998,0.19962,0.30028],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.29196,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.06746,0.03988],"object_pos_start":[0.50305,0.06746,0.03996],"object_to_goal_dist_end":0.14749,"object_to_goal_dist_start":0.14749,"object_z_max":0.03996,"peak_contact_force":0.0,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"push_through_channel","tcp_end":[0.49973,0.19959,0.30009],"tcp_start":[0.49976,0.1996,0.30017],"tcp_to_object_dist_end":0.29185,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7acce370299b32aeef0e4239da3e97eae076cb9602edead185a6cf774ee0bc4e`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,-0.04822,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,-0.04822,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.34375,"average_solve_count":64.0,"average_success_count":64.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.19317,"approach_peg.approach_tolerance":0.01422,"push_along_channel.force_threshold":15.68996,"push_along_channel.push_distance":0.13964,"push_along_channel.push_speed":0.08838},"optimized_scores":{"best_composite_score":0.96443,"best_fitness_score":0.71443,"best_task_score":0.60118},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":779.0,"contact_point_centroid":[0.50378,0.11135,0.00934],"force_p95":0.85912,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":120.9001,"mean_force":3.10246,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50213,0.16589,0.16894]},{"body_a":"attachment","body_b":"peg","contact_count":30.0,"contact_point_centroid":[0.51056,0.12697,0.05701],"force_p95":118.37169,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":120.42011,"mean_force":66.35668,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.5062,0.13722,0.05793]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54349,-0.00982,0.06],"force_p95":27.09887,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":27.09887,"mean_force":27.09887,"phase_index":1.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49872,-0.00508,0.03697]},{"body_a":"attachment","body_b":"peg","contact_count":569.0,"contact_point_centroid":[0.499,0.03646,0.03996],"force_p95":5.16951,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.79054,"mean_force":1.53787,"phase_index":1.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50029,0.04832,0.0393]},{"body_a":"peg","body_b":"channel_base_body","contact_count":944.0,"contact_point_centroid":[0.49648,0.02259,0.00938],"force_p95":3.00144,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.65226,"mean_force":1.08909,"phase_index":1.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.5009,0.06444,0.04014]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":133.0,"contact_point_centroid":[0.47498,-0.00855,0.02753],"force_p95":5.14773,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.59533,"mean_force":2.96423,"phase_index":1.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50035,0.05039,0.03939]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49973,0.19939,0.29894]}],"total_contact_groups":7},"final_pose_error":0.03855,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49561,-0.04209,0.02769],"final_tcp_position":[0.49872,-0.00537,0.03697],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":120.9001,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":801.0,"n_steps_budget":870.0,"object_pos_end":[0.50174,0.09597,0.04015],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.17598,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.20637,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":825.0,"raw_peak_contact_force":120.9001,"subtask_id":"reach_contact","tcp_end":[0.50686,0.13493,0.04809],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04008,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":977.0,"n_steps_budget":1000.0,"object_pos_end":[0.49561,-0.04209,0.02769],"object_pos_start":[0.50174,0.09597,0.04015],"object_to_goal_dist_end":0.0401,"object_to_goal_dist_start":0.17598,"object_z_max":0.04088,"peak_contact_force":27.09887,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1647.0,"raw_peak_contact_force":27.09887,"subtask_id":"push_through_channel","tcp_end":[0.49872,-0.00537,0.03697],"tcp_start":[0.50686,0.13493,0.04809],"tcp_to_object_dist_end":0.038,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```