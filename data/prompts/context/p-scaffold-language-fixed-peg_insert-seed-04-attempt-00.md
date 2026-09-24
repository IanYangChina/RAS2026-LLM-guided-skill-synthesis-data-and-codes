## Search State

- **Seed**: 4
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.3815 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.00 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `03ab66c73c39e70252b7764557f10cd17ad49cc08b28e1c3cb573bd8dcea88ba`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.5354444884457894, 0.000906204225148928, 0.08]
- Frozen socket pose: [0.5354444884457894, 0.000906204225148928, 0.025] (static fixture for this episode)
- Goal object position: (0.5354444884457894, 0.000906204225148928, 0.025)
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
  frozen_task_target: [0.5354, 0.0009, 0.08]
  frozen_socket_position: [0.5354, 0.0009, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.5354444884457894, 0.000906204225148928, 0.08]}
  frozen_fixtures: {'peg_socket': [0.5354444884457894, 0.000906204225148928, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: 03ab66c73c39e70252b7764557f10cd17ad49cc08b28e1c3cb573bd8dcea88ba

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| align | object | (0.00, 0.00, 0.12) | distance | — |
| approach | object | (0.00, 0.00, 0.09) | distance | — |
| contact | object | (0.00, 0.00, 0.07) | distance | — |
| insert | object | (0.00, 0.00, 0.06) | distance | — |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=-0.381) — your mutation base

```yaml
skill: peg_insert
phases:
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
- id: insert_1
  type: insert
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  parameters:
    insertion_force:
      type: scalar
      range:
      - 1.0
      - 20.0
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
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: -0.381
- **task_score** (E): 0.000
- **fitness_score**: 0.059  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 0.00 | 0.1532 |
| approach_1 | 1.00 | 0.00 | 0.1133 |
| contact_1 | 0.00 | 0.00 | 0.0266 |
| insert_1 | 1.00 | 0.00 | 0.0819 |
| retract_1 | 0.00 | 0.00 | 0.1282 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.503, -0.000, 0.454) | (0.504, -0.000, 0.340)→(0.496, 0.000, 0.493) | 0.260→0.413 | 0.00 / 0.000 | 0.000 | 0.000 |
| approach_1 | approach | 1.00 / step_budget | (0.503, -0.000, 0.454)→(0.497, 0.000, 0.567) | (0.496, 0.000, 0.493)→(0.481, 0.000, 0.604) | 0.413→0.524 | 0.00 / 0.000 | 0.000 | 0.000 |
| contact_1 | contact | 0.00 / step_budget | (0.497, 0.000, 0.567)→(0.492, 0.000, 0.593) | (0.481, 0.000, 0.604)→(0.475, 0.000, 0.629) | 0.524→0.550 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_1 | insert | 1.00 / step_budget | (0.492, 0.000, 0.593)→(0.477, 0.000, 0.674) | (0.475, 0.000, 0.629)→(0.454, 0.000, 0.706) | 0.550→0.628 | 0.00 / 0.000 | 0.000 | 0.000 |
| retract_1 | retract | 0.00 / step_budget | (0.477, 0.000, 0.674)→(0.467, 0.026, 0.799) | (0.454, 0.000, 0.706)→(0.435, 0.025, 0.823) | 0.628→0.746 | 0.00 / 0.000 | 0.000 | 0.000 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.000
- alignment_error: None
- force_efficiency: 1.000
- terminal_score: 0.000
- phase_score: 0.097
- phase_breakdown.insert_score: 0.004
- phase_breakdown.align_score: 0.792
- phase_breakdown.contact_score: 0.023
- phase_breakdown.approach_score: 0.059

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.059
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.381
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: tolflatfitness
- **Mean generations**: 5.0
- **Final σ (mean)**: 0.383


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `9dafd9212fa57d4ed6b507cf5ac09991f034abfc2fa41dbd37d7c702246c6284`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5ab22a59b7a3c9c0e28c9743e3882e986d7ba7a97654ba206ec4bffa38a24163`; realized-scene SHA-256: `03ab66c73c39e70252b7764557f10cd17ad49cc08b28e1c3cb573bd8dcea88ba`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.53544,0.00091,0.025]},{"name":"target","value":[0.53544,0.00091,0.025]},{"name":"socket","value":[0.53544,0.00091,0.025]},{"name":"goal","value":[0.53544,0.00091,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.00091,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.53544,0.00091,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.15607,"average_solve_count":173.0,"average_success_count":173.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-0.00117,"approach_1.approach_height":0.25671,"contact_1.contact_force":11.98517,"contact_1.speed":0.01645,"insert_1.insertion_force":8.66032,"retract_1.retract_height":0.07874,"retract_1.speed":0.05251},"optimized_scores":{"best_composite_score":-0.38146,"best_fitness_score":0.05854,"best_task_score":0.00012},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.13528,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.46677,0.0259,0.79878],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":935.0,"n_steps_budget":1000.0,"object_pos_end":[0.4963,1e-05,0.49311],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.41312,"object_to_goal_dist_start":0.26034,"object_z_max":0.49298,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50307,-0.0,0.45368],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.48128,5e-05,0.60366],"object_pos_start":[0.4963,1e-05,0.49311],"object_to_goal_dist_end":0.52399,"object_to_goal_dist_start":0.41312,"object_z_max":0.60353,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49683,3e-05,0.5668],"tcp_start":[0.50307,-0.0,0.45368],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47491,9e-05,0.629],"object_pos_start":[0.48128,5e-05,0.60366],"object_to_goal_dist_end":0.54957,"object_to_goal_dist_start":0.52399,"object_z_max":0.62897,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49243,5e-05,0.59304],"tcp_start":[0.49683,3e-05,0.5668],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.45355,0.00016,0.70593],"object_pos_start":[0.47491,9e-05,0.629],"object_to_goal_dist_end":0.62765,"object_to_goal_dist_start":0.54957,"object_z_max":0.70582,"peak_contact_force":0.0,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.47697,0.00012,0.67351],"tcp_start":[0.49243,5e-05,0.59304],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43481,0.02473,0.8228],"object_pos_start":[0.45355,0.00016,0.70593],"object_to_goal_dist_end":0.74607,"object_to_goal_dist_start":0.62765,"object_z_max":0.82269,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.46677,0.0259,0.79878],"tcp_start":[0.47697,0.00012,0.67351],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1cd3bcde9ecee8889beeec63bba6949652ce08dd1277aacff8bc717cc59ca677`; realized-scene SHA-256: `3a693f0216d44408acf55cd4ed5e7511210ea06892083b191557e74fdeb42bf8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.5244,0.02464,0.025]},{"name":"target","value":[0.5244,0.02464,0.025]},{"name":"socket","value":[0.5244,0.02464,0.025]},{"name":"goal","value":[0.5244,0.02464,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.02464,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.5244,0.02464,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.14754,"average_solve_count":183.0,"average_success_count":183.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-0.00177,"approach_1.approach_height":0.18329,"contact_1.contact_force":15.7802,"contact_1.speed":0.0141,"insert_1.insertion_force":11.73939,"retract_1.retract_height":0.15476,"retract_1.speed":0.04193},"optimized_scores":{"best_composite_score":-0.38146,"best_fitness_score":0.05854,"best_task_score":0.00012},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.13624,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.46685,0.0259,0.79781],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":935.0,"n_steps_budget":1000.0,"object_pos_end":[0.4963,1e-05,0.49311],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.41312,"object_to_goal_dist_start":0.26034,"object_z_max":0.49298,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50307,-0.0,0.45368],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.48128,5e-05,0.60366],"object_pos_start":[0.4963,1e-05,0.49311],"object_to_goal_dist_end":0.52399,"object_to_goal_dist_start":0.41312,"object_z_max":0.60353,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49683,3e-05,0.5668],"tcp_start":[0.50307,-0.0,0.45368],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47491,9e-05,0.629],"object_pos_start":[0.48128,5e-05,0.60366],"object_to_goal_dist_end":0.54957,"object_to_goal_dist_start":0.52399,"object_z_max":0.62897,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49243,5e-05,0.59304],"tcp_start":[0.49683,3e-05,0.5668],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.45355,0.00016,0.70593],"object_pos_start":[0.47491,9e-05,0.629],"object_to_goal_dist_end":0.62765,"object_to_goal_dist_start":0.54957,"object_z_max":0.70582,"peak_contact_force":0.0,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.47697,0.00012,0.67351],"tcp_start":[0.49243,5e-05,0.59304],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43495,0.02474,0.82191],"object_pos_start":[0.45355,0.00016,0.70593],"object_to_goal_dist_end":0.74517,"object_to_goal_dist_start":0.62765,"object_z_max":0.8218,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.46685,0.0259,0.79781],"tcp_start":[0.47697,0.00012,0.67351],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `3a12d7f15d1e6c6a0af002631f15bc7a534f5434829fc9db32b3974b909f1f84`; realized-scene SHA-256: `72d0fc56eb607f902ea78d3570decababa6da9acffffae87b8c65460ac3ff15e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.50305,-0.01254,0.025]},{"name":"target","value":[0.50305,-0.01254,0.025]},{"name":"socket","value":[0.50305,-0.01254,0.025]},{"name":"goal","value":[0.50305,-0.01254,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,-0.01254,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.50305,-0.01254,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.15976,"average_solve_count":169.0,"average_success_count":169.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-0.00047,"approach_1.approach_height":0.19151,"contact_1.contact_force":8.60423,"contact_1.speed":0.01699,"insert_1.insertion_force":13.77676,"retract_1.retract_height":0.14801,"retract_1.speed":0.05796},"optimized_scores":{"best_composite_score":-0.38146,"best_fitness_score":0.05854,"best_task_score":0.00012},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.13459,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.46672,0.0259,0.79948],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":935.0,"n_steps_budget":1000.0,"object_pos_end":[0.4963,1e-05,0.49311],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.41312,"object_to_goal_dist_start":0.26034,"object_z_max":0.49298,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50307,-0.0,0.45368],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.48128,5e-05,0.60366],"object_pos_start":[0.4963,1e-05,0.49311],"object_to_goal_dist_end":0.52399,"object_to_goal_dist_start":0.41312,"object_z_max":0.60353,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49683,3e-05,0.5668],"tcp_start":[0.50307,-0.0,0.45368],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47491,9e-05,0.629],"object_pos_start":[0.48128,5e-05,0.60366],"object_to_goal_dist_end":0.54957,"object_to_goal_dist_start":0.52399,"object_z_max":0.62897,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49243,5e-05,0.59304],"tcp_start":[0.49683,3e-05,0.5668],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.45355,0.00016,0.70593],"object_pos_start":[0.47491,9e-05,0.629],"object_to_goal_dist_end":0.62765,"object_to_goal_dist_start":0.54957,"object_z_max":0.70582,"peak_contact_force":0.0,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.47697,0.00012,0.67351],"tcp_start":[0.49243,5e-05,0.59304],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43472,0.02473,0.82345],"object_pos_start":[0.45355,0.00016,0.70593],"object_to_goal_dist_end":0.74672,"object_to_goal_dist_start":0.62765,"object_z_max":0.82332,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.46672,0.0259,0.79948],"tcp_start":[0.47697,0.00012,0.67351],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```