## Search State

- **Seed**: 3
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → align → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4843 | 0.86 | ❌ rejected |
| 4 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.7464 | 0.96 | ❌ rejected |
| 3 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.7464 | 0.96 | ❌ rejected |
| 2 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.7464 | 0.96 | ❌ rejected |
| 1 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.7464 | 0.96 | ❌ rejected |

**Proposal policy**: task_score is 0.86 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `3a9889f49656bcc88af2945ad0b69da740661b3d51c4f32509721809854ac75e`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.46685193337148995, -0.021055159472312023, 0.08]
- Frozen socket pose: [0.46685193337148995, -0.021055159472312023, 0.025] (static fixture for this episode)
- Goal object position: (0.46685193337148995, -0.021055159472312023, 0.025)
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
  frozen_task_target: [0.4669, -0.0211, 0.08]
  frozen_socket_position: [0.4669, -0.0211, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.46685193337148995, -0.021055159472312023, 0.08]}
  frozen_fixtures: {'peg_socket': [0.46685193337148995, -0.021055159472312023, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: 3a9889f49656bcc88af2945ad0b69da740661b3d51c4f32509721809854ac75e

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.956, which indicates the subtask decomposition is already effective.
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
| `goal` | offset from task goal position (0.46685193337148995, -0.021055159472312023, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (0.46685193337148995, -0.021055159472312023, 0.025) | approach/contact targets near fixture |

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

## Current Skill (Q=0.484) — your mutation base

```yaml
skill: peg_insert
phases:
- id: rotate_1
  type: rotate
  generator: impedance_motion
  control: position_control
  termination: pose_tolerance
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  parameters:
    depth:
      type: scalar
      range:
      - 0.01
      - 0.1
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

```

## Design Metrics

- **Composite score**: 0.484
- **task_score** (E): 0.865
- **fitness_score**: 0.714  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_socket | 1.00 | 0.00 | 0.1320 |
| align_entry | 1.00 | 0.00 | 0.0646 |
| insert_into_socket | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_socket | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.505, 0.001, 0.172) | (0.504, -0.000, 0.340)→(0.506, 0.001, 0.212) | 0.260→0.136 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_entry | align | 1.00 / step_budget | (0.505, 0.001, 0.172)→(0.496, 0.005, 0.109) | (0.506, 0.001, 0.212)→(0.497, 0.005, 0.149) | 0.136→0.075 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_into_socket | insert | 0.00 / guard_failure | (0.502, 0.002, 0.050)→(0.502, 0.002, 0.050) | (0.497, 0.005, 0.149)→(0.503, 0.002, 0.090) | 0.075→0.034 | 1.00 / 1.000 | 112.355 | 245.077 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.908
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.908
- phase_score: 0.642
- phase_breakdown.approach_above_score: 0.836
- phase_breakdown.insertion_score: 0.594

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.749
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.908
- **Median Q (composite search score)**: 0.504
- **K-run variance**: 0.0015
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.372


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `f11800d9c2e1994b03c35d775c68a936832c378ea82102a5404a99f161f65289`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5ef8adc000d20c9595fb92eedb002c99ab6f0fb118834572ef2a426eae092b67`; realized-scene SHA-256: `3a9889f49656bcc88af2945ad0b69da740661b3d51c4f32509721809854ac75e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.46685,-0.02106,0.025]},{"name":"target","value":[0.46685,-0.02106,0.025]},{"name":"socket","value":[0.46685,-0.02106,0.025]},{"name":"goal","value":[0.46685,-0.02106,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,-0.02106,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.46685,-0.02106,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90141,"average_solve_count":71.0,"average_success_count":71.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_entry.lateral_offset_x":-0.00587,"align_entry.lateral_offset_y":0.01744,"approach_socket.approach_height":0.13958,"insert_into_socket.insertion_depth":0.0665},"optimized_scores":{"best_composite_score":0.43063,"best_fitness_score":0.66063,"best_task_score":0.80629},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.47669,-0.018,0.04991],"force_p95":224.52998,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":231.04832,"mean_force":165.86496,"phase_index":2.0,"phase_name":"insert_into_socket","phase_type":"insert","tcp_position_centroid":[0.4617,-0.01758,0.04997]}],"total_contact_groups":1},"final_pose_error":0.01281,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.4618,-0.01765,0.04976],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":231.04832,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":398.0,"n_steps_budget":900.0,"object_pos_end":[0.46795,-0.01883,0.21418],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.13923,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_above","tcp_end":[0.46754,-0.01882,0.17418],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":347.0,"n_steps_budget":600.0,"object_pos_end":[0.45887,-0.00532,0.14891],"object_pos_start":[0.46795,-0.01883,0.21418],"object_to_goal_dist_end":0.08043,"object_to_goal_dist_start":0.13923,"object_z_max":0.21418,"peak_contact_force":0.0,"phase_name":"align_entry","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.45846,-0.00532,0.10892],"tcp_start":[0.46754,-0.01882,0.17418],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":220.0,"n_steps_budget":600.0,"object_pos_end":[0.46214,-0.01762,0.08986],"object_pos_start":[0.45887,-0.00532,0.14891],"object_to_goal_dist_end":0.04291,"object_to_goal_dist_start":0.08043,"object_z_max":0.14891,"peak_contact_force":100.6816,"phase_name":"insert_into_socket","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":231.04832,"subtask_id":"insertion","tcp_end":[0.4618,-0.01765,0.04976],"tcp_start":[0.46173,-0.01761,0.04986],"tcp_to_object_dist_end":0.0401,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `3e77e957595308cac760f5f4d0307201511ded613ae0a20d2d9d48ef360ca4f0`; realized-scene SHA-256: `03ab66c73c39e70252b7764557f10cd17ad49cc08b28e1c3cb573bd8dcea88ba`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.53544,0.00091,0.025]},{"name":"target","value":[0.53544,0.00091,0.025]},{"name":"socket","value":[0.53544,0.00091,0.025]},{"name":"goal","value":[0.53544,0.00091,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.00091,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.53544,0.00091,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78571,"average_solve_count":70.0,"average_success_count":70.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_entry.lateral_offset_x":-0.01537,"align_entry.lateral_offset_y":-0.00298,"approach_socket.approach_height":0.13592,"insert_into_socket.insertion_depth":0.06986},"optimized_scores":{"best_composite_score":0.51872,"best_fitness_score":0.74872,"best_task_score":0.90814},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.54187,0.00023,0.04987],"force_p95":334.00201,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":345.72393,"mean_force":228.50479,"phase_index":2.0,"phase_name":"insert_into_socket","phase_type":"insert","tcp_position_centroid":[0.52687,0.00014,0.04992]}],"total_contact_groups":1},"final_pose_error":0.0169,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.52696,0.00015,0.04973],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":345.72393,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":443.0,"n_steps_budget":900.0,"object_pos_end":[0.52959,0.00079,0.20862],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.13199,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_above","tcp_end":[0.52911,0.00078,0.16863],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":280.0,"n_steps_budget":600.0,"object_pos_end":[0.51829,-0.00169,0.14928],"object_pos_start":[0.52959,0.00079,0.20862],"object_to_goal_dist_end":0.07167,"object_to_goal_dist_start":0.13199,"object_z_max":0.20862,"peak_contact_force":0.0,"phase_name":"align_entry","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.51781,-0.00169,0.10928],"tcp_start":[0.52911,0.00078,0.16863],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":212.0,"n_steps_budget":600.0,"object_pos_end":[0.52738,0.00015,0.08981],"object_pos_start":[0.51829,-0.00169,0.14928],"object_to_goal_dist_end":0.02909,"object_to_goal_dist_start":0.07167,"object_z_max":0.14928,"peak_contact_force":111.28565,"phase_name":"insert_into_socket","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":345.72393,"subtask_id":"insertion","tcp_end":[0.52696,0.00015,0.04973],"tcp_start":[0.5269,0.00015,0.04981],"tcp_to_object_dist_end":0.04008,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f1677605f38c34d5c76967e3b08a88589314d198860b89f86514cd0f3e96f4b3`; realized-scene SHA-256: `3a693f0216d44408acf55cd4ed5e7511210ea06892083b191557e74fdeb42bf8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.5244,0.02464,0.025]},{"name":"target","value":[0.5244,0.02464,0.025]},{"name":"socket","value":[0.5244,0.02464,0.025]},{"name":"goal","value":[0.5244,0.02464,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.02464,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.5244,0.02464,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89855,"average_solve_count":69.0,"average_success_count":69.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_entry.lateral_offset_x":-0.00893,"align_entry.lateral_offset_y":-0.00216,"approach_socket.approach_height":0.14159,"insert_into_socket.insertion_depth":0.0699},"optimized_scores":{"best_composite_score":0.50355,"best_fitness_score":0.73355,"best_task_score":0.88006},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.53247,0.02476,0.04988],"force_p95":156.78993,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":158.45786,"mean_force":141.77855,"phase_index":2.0,"phase_name":"insert_into_socket","phase_type":"insert","tcp_position_centroid":[0.51751,0.02378,0.04994]}],"total_contact_groups":1},"final_pose_error":0.01614,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.51754,0.02378,0.04968],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":158.45786,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":418.0,"n_steps_budget":870.0,"object_pos_end":[0.5195,0.02209,0.21462],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.13781,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_above","tcp_end":[0.51903,0.02207,0.17462],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":314.0,"n_steps_budget":600.0,"object_pos_end":[0.51288,0.02226,0.14894],"object_pos_start":[0.5195,0.02209,0.21462],"object_to_goal_dist_end":0.07358,"object_to_goal_dist_start":0.13781,"object_z_max":0.21462,"peak_contact_force":0.0,"phase_name":"align_entry","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.51243,0.02224,0.10894],"tcp_start":[0.51903,0.02207,0.17462],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":204.0,"n_steps_budget":600.0,"object_pos_end":[0.51801,0.02381,0.08981],"object_pos_start":[0.51288,0.02226,0.14894],"object_to_goal_dist_end":0.03142,"object_to_goal_dist_start":0.07358,"object_z_max":0.14894,"peak_contact_force":125.09924,"phase_name":"insert_into_socket","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":158.45786,"subtask_id":"insertion","tcp_end":[0.51754,0.02378,0.04968],"tcp_start":[0.51755,0.02378,0.04981],"tcp_to_object_dist_end":0.04013,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```