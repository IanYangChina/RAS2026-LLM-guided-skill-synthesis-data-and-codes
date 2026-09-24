## Search State

- **Seed**: 9
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | 0.4018 | 0.77 | ❌ rejected |
| 1 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | 0.4018 | 0.77 | ❌ rejected |
| 0 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | 0.4018 | 0.77 | ✅ accepted |

**Proposal policy**: task_score is 0.77 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: peg_insert
- Frozen realised-scene SHA-256: `b79f8c48d80d518422f0f353e5fb8a66ede3bec4fd1cbe80690c422c72d900f9`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.5296199363176062, -0.017054623272995572, 0.08]
- Frozen socket pose: [0.5296199363176062, -0.017054623272995572, 0.025] (static fixture for this episode)
- Goal object position: (0.5296199363176062, -0.017054623272995572, 0.025)
- Object initial pose: (0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 40.0 N
- Channel axis: `(0.0, 0.0, -1.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth ratio (axial progress into hole)**

## Scene Entities

robot:
  model: panda_peg
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: peg_socket
    role: fixture
    dynamics: static
    geometry: box_with_hole
    base_dimensions_m: [0.12, 0.12, 0.05]
    hole_entry_height_m: 0.08
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    note: peg is a fixed end-effector attachment on the panda_peg arm
task_landmarks:
  frozen_object_start: [0.504, -0, 0.3403]
  frozen_task_target: [0.5296, -0.0171, 0.08]
  frozen_socket_position: [0.5296, -0.0171, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.5296199363176062, -0.017054623272995572, 0.08]}
  frozen_fixtures: {'peg_socket': [0.5296199363176062, -0.017054623272995572, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: b79f8c48d80d518422f0f353e5fb8a66ede3bec4fd1cbe80690c422c72d900f9

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.772, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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
| `object` | offset from object initial position (0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5296199363176062, -0.017054623272995572, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (0.5296199363176062, -0.017054623272995572, 0.025) | approach/contact targets near fixture |

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

## Current Skill (Q=0.402) — your mutation base

```yaml
skill: peg_insert
skill_type: arm_gripper
phases:
- id: rotate_1
  type: rotate
  generator: arc_cartesian
  control: impedance_control
  termination: time_limit
- id: pull_1
  type: pull
  generator: arc_cartesian
  control: impedance_control
  termination: time_limit
  parameters:
    pull_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
- id: push_1
  type: push
  generator: impedance_motion
  control: position_control
  termination: time_limit
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
- id: descend_2
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: contact_detected
- id: grasp_1
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  parameters:
    grip_force:
      type: scalar
      range:
      - 5.0
      - 30.0

```

## Design Metrics

- **Composite score**: 0.402
- **task_score** (E): 0.772
- **fitness_score**: 0.772  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.370

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| rotate_1 | 1.00 | 0.0411 |
| pull_1 | 1.00 | 0.0033 |
| push_1 | 1.00 | 0.2139 |
| descend_1 | 1.00 | 0.1119 |
| descend_2 | 0.00 | 0.1127 |
| grasp_1 | 1.00 | 0.0087 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| rotate_1 | rotate | 1.00 / time_limit | (0.500, -0.000, 0.301)→(0.498, 0.003, 0.342) | (0.504, -0.000, 0.340)→(0.500, 0.003, 0.382) | 0.260→0.302 |
| pull_1 | pull | 1.00 / time_limit | (0.498, 0.003, 0.342)→(0.498, 0.001, 0.344) | (0.500, 0.003, 0.382)→(0.500, 0.001, 0.384) | 0.302→0.304 |
| push_1 | push | 1.00 / time_limit | (0.498, 0.001, 0.344)→(0.496, 0.000, 0.130) | (0.500, 0.001, 0.384)→(0.508, 0.000, 0.169) | 0.304→0.089 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.000, 0.130)→(0.505, 0.000, 0.242) | (0.508, 0.000, 0.169)→(0.512, 0.000, 0.281) | 0.089→0.202 |
| descend_2 | descend | 0.00 / step_budget | (0.505, 0.000, 0.242)→(0.510, 0.000, 0.355) | (0.512, 0.000, 0.281)→(0.510, 0.000, 0.395) | 0.202→0.315 |
| grasp_1 | grasp | 1.00 / step_budget | (0.510, 0.000, 0.355)→(0.507, 0.000, 0.346) | (0.510, 0.000, 0.395)→(0.508, 0.000, 0.386) | 0.315→0.307 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.772
- alignment_error: None

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.772
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.772
- **Median Q (composite search score)**: 0.402
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Parameters at upper bound**: push_1.push_speed
- **Final σ (mean)**: 0.406


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `ad55441961509110caa3e00662ff00c043a366a9841ef346adcb2ae98eb0fa2d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `848090e975b2909410760ed4539d133eb61635ea5a8640e3622d2871416125a9`; realized-scene SHA-256: `b79f8c48d80d518422f0f353e5fb8a66ede3bec4fd1cbe80690c422c72d900f9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.52962,-0.01705,0.025]},{"name":"target","value":[0.52962,-0.01705,0.025]},{"name":"socket","value":[0.52962,-0.01705,0.025]},{"name":"goal","value":[0.52962,-0.01705,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,-0.01705,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.52962,-0.01705,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.46715,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"grasp_1.grip_force":18.32457,"pull_1.pull_distance":0.18545,"push_1.push_depth":0.05437,"push_1.push_distance":0.05053,"push_1.push_speed":0.09993},"optimized_scores":{"best_composite_score":0.40183,"best_fitness_score":0.77183,"best_task_score":0.77183},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.01193,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.50986,0.00012,0.35462],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"phases":[{"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49989,0.0026,0.3815],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.30151,"object_to_goal_dist_start":0.26034,"object_z_max":0.38144,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","tcp_end":[0.49823,0.00259,0.34154],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":339.0,"n_steps_budget":600.0,"object_pos_end":[0.49956,0.00089,0.38431],"object_pos_start":[0.49989,0.0026,0.3815],"object_to_goal_dist_end":0.30431,"object_to_goal_dist_start":0.30151,"object_z_max":0.3843,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","tcp_end":[0.49808,0.00087,0.34434],"tcp_start":[0.49823,0.00259,0.34154],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50815,0.00015,0.16861],"object_pos_start":[0.49956,0.00089,0.38431],"object_to_goal_dist_end":0.08898,"object_to_goal_dist_start":0.30431,"object_z_max":0.38431,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.49609,0.00012,0.13047],"tcp_start":[0.49808,0.00087,0.34434],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":702.0,"n_steps_budget":780.0,"object_pos_end":[0.51181,0.00014,0.28139],"object_pos_start":[0.50815,0.00015,0.16861],"object_to_goal_dist_end":0.20174,"object_to_goal_dist_start":0.08898,"object_z_max":0.28126,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.50495,0.00011,0.24199],"tcp_start":[0.49609,0.00012,0.13047],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":722.0,"n_steps_budget":780.0,"object_pos_end":[0.50977,0.00016,0.39462],"object_pos_start":[0.51181,0.00014,0.28139],"object_to_goal_dist_end":0.31477,"object_to_goal_dist_start":0.20174,"object_z_max":0.39449,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.50986,0.00012,0.35462],"tcp_start":[0.50495,0.00011,0.24199],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50769,0.00015,0.38642],"object_pos_start":[0.50977,0.00016,0.39462],"object_to_goal_dist_end":0.30651,"object_to_goal_dist_start":0.31477,"object_z_max":0.39472,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.50707,9e-05,0.34642],"tcp_start":[0.50986,0.00012,0.35462],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `86374ae559fdd7367448730b4cd37979be4c5ee1e51a6d45d322ddd67c264ad8`; realized-scene SHA-256: `77fea26f11e91c54ae4a9c1f03cd5e6af1b4f6cac3191aa4cbd28ae81b548c93`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.53648,-0.02339,0.025]},{"name":"target","value":[0.53648,-0.02339,0.025]},{"name":"socket","value":[0.53648,-0.02339,0.025]},{"name":"goal","value":[0.53648,-0.02339,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,-0.02339,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.53648,-0.02339,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.46715,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"grasp_1.grip_force":16.93184,"pull_1.pull_distance":0.09322,"push_1.push_depth":0.07887,"push_1.push_distance":0.07011,"push_1.push_speed":0.09988},"optimized_scores":{"best_composite_score":0.40183,"best_fitness_score":0.77183,"best_task_score":0.77183},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.01193,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.50986,0.00012,0.35462],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"phases":[{"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49989,0.0026,0.3815],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.30151,"object_to_goal_dist_start":0.26034,"object_z_max":0.38144,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","tcp_end":[0.49823,0.00259,0.34154],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":339.0,"n_steps_budget":600.0,"object_pos_end":[0.49956,0.00089,0.38431],"object_pos_start":[0.49989,0.0026,0.3815],"object_to_goal_dist_end":0.30431,"object_to_goal_dist_start":0.30151,"object_z_max":0.3843,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","tcp_end":[0.49808,0.00087,0.34434],"tcp_start":[0.49823,0.00259,0.34154],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50815,0.00015,0.16861],"object_pos_start":[0.49956,0.00089,0.38431],"object_to_goal_dist_end":0.08898,"object_to_goal_dist_start":0.30431,"object_z_max":0.38431,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.49609,0.00012,0.13047],"tcp_start":[0.49808,0.00087,0.34434],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":702.0,"n_steps_budget":780.0,"object_pos_end":[0.51181,0.00014,0.28139],"object_pos_start":[0.50815,0.00015,0.16861],"object_to_goal_dist_end":0.20174,"object_to_goal_dist_start":0.08898,"object_z_max":0.28126,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.50495,0.00011,0.24199],"tcp_start":[0.49609,0.00012,0.13047],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":722.0,"n_steps_budget":780.0,"object_pos_end":[0.50977,0.00016,0.39462],"object_pos_start":[0.51181,0.00014,0.28139],"object_to_goal_dist_end":0.31477,"object_to_goal_dist_start":0.20174,"object_z_max":0.39449,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.50986,0.00012,0.35462],"tcp_start":[0.50495,0.00011,0.24199],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50769,0.00015,0.38642],"object_pos_start":[0.50977,0.00016,0.39462],"object_to_goal_dist_end":0.30651,"object_to_goal_dist_start":0.31477,"object_z_max":0.39472,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.50707,9e-05,0.34642],"tcp_start":[0.50986,0.00012,0.35462],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `caf3f4690e3f1b09696902a0a7669c72f02512d93a4ac4443caef9efffcf46f7`; realized-scene SHA-256: `6cd5caaafe0ec0cc23a4551cd60416799cdbf9885c1214f7b258fb3313892a60`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.47029,-6e-05,0.025]},{"name":"target","value":[0.47029,-6e-05,0.025]},{"name":"socket","value":[0.47029,-6e-05,0.025]},{"name":"goal","value":[0.47029,-6e-05,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.47029,-6e-05,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.47029,-6e-05,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.46715,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"grasp_1.grip_force":5.81742,"pull_1.pull_distance":0.09238,"push_1.push_depth":0.09988,"push_1.push_distance":0.07871,"push_1.push_speed":0.1},"optimized_scores":{"best_composite_score":0.40183,"best_fitness_score":0.77183,"best_task_score":0.77183},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.01193,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.47029,-6e-05,0.025],"final_tcp_position":[0.50986,0.00012,0.35462],"realised_fixture_position":[0.47029,-6e-05,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.47029,-6e-05,0.08]},"phases":[{"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49989,0.0026,0.3815],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.30151,"object_to_goal_dist_start":0.26034,"object_z_max":0.38144,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","tcp_end":[0.49823,0.00259,0.34154],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":339.0,"n_steps_budget":600.0,"object_pos_end":[0.49956,0.00089,0.38431],"object_pos_start":[0.49989,0.0026,0.3815],"object_to_goal_dist_end":0.30431,"object_to_goal_dist_start":0.30151,"object_z_max":0.3843,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","tcp_end":[0.49808,0.00087,0.34434],"tcp_start":[0.49823,0.00259,0.34154],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50815,0.00015,0.16861],"object_pos_start":[0.49956,0.00089,0.38431],"object_to_goal_dist_end":0.08898,"object_to_goal_dist_start":0.30431,"object_z_max":0.38431,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.49609,0.00012,0.13047],"tcp_start":[0.49808,0.00087,0.34434],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":702.0,"n_steps_budget":780.0,"object_pos_end":[0.51181,0.00014,0.28139],"object_pos_start":[0.50815,0.00015,0.16861],"object_to_goal_dist_end":0.20174,"object_to_goal_dist_start":0.08898,"object_z_max":0.28126,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.50495,0.00011,0.24199],"tcp_start":[0.49609,0.00012,0.13047],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":722.0,"n_steps_budget":780.0,"object_pos_end":[0.50977,0.00016,0.39462],"object_pos_start":[0.51181,0.00014,0.28139],"object_to_goal_dist_end":0.31477,"object_to_goal_dist_start":0.20174,"object_z_max":0.39449,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.50986,0.00012,0.35462],"tcp_start":[0.50495,0.00011,0.24199],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50769,0.00015,0.38642],"object_pos_start":[0.50977,0.00016,0.39462],"object_to_goal_dist_end":0.30651,"object_to_goal_dist_start":0.31477,"object_z_max":0.39472,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.50707,9e-05,0.34642],"tcp_start":[0.50986,0.00012,0.35462],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```