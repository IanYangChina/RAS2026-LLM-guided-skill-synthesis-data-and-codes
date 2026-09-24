## Search State

- **Seed**: 7
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → retract → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 9 | 0.0765 | 0.87 | ✅ accepted |
| 1 | approach → grasp → retract → approach → align → descend | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | force_threshold_switch | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 7 | 0.1778 | 0.85 | ✅ accepted |
| 0 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.2960 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.87 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 40.0 N
- Primary evaluation target: **insertion depth ratio (axial progress into hole)**

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
| `object` | offset from object initial position | approach/contact targets near object start |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose | approach/contact targets near fixture |

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

## Current Skill (Q=0.076) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_peg
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.2
- id: approach_hole
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.3
- id: insert_task
  weight: 0.5
phases:
- id: approach_peg
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.005
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_peg
- id: descend_to_peg
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.005
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 2.0
      - 15.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.003
    - 0.003
    - 0.0
- id: grasp_peg
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
- id: lift_peg
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.005
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
- id: approach_hole
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.005
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_hole
- id: align_hole
  type: align
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.003
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
- id: descend_insert
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.06
      axis: world_z
      mode: replace_offset_projection
      sign: negative
    tolerance: 0.005
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    force_threshold:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 15.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    insertion_depth:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.06
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  retries:
    max_attempts: 3
    strategy: offset_target
    offset:
    - 0.003
    - 0.003
    - 0.0
  subtask_id: insert_task

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.05], tolerance=0.005
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_peg** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.003, 0.003, 0.0]
- **grasp_peg** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]
- **lift_peg** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.05], tolerance=0.005
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **approach_hole** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.005
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **align_hole** (`align`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.02], tolerance=0.003
  - parameter_bindings:
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
- **descend_insert** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.06, mode=replace_offset_projection, sign=negative}, tolerance=0.005
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - retries: max_attempts=3, strategy=offset_target, offset=[0.003, 0.003, 0.0]

## Design Metrics

- **Composite score**: 0.076
- **task_score** (E): 0.869
- **fitness_score**: 0.629  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.048
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.600

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 0.00 | 0.0800 |
| descend_to_peg | 0.00 | 0.00 | 0.0278 |
| grasp_peg | 1.00 | 0.00 | 0.0083 |
| lift_peg | 1.00 | 0.00 | 0.0177 |
| approach_hole | 0.00 | 0.00 | 0.2007 |
| align_hole | 1.00 | 0.00 | 0.1172 |
| descend_insert | 0.33 | 0.33 | 0.0188 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.502, -0.000, 0.380) | (0.504, -0.000, 0.340)→(0.501, -0.000, 0.420) | 0.260→0.340 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_to_peg | descend | 0.00 / step_budget | (0.502, -0.000, 0.380)→(0.500, -0.000, 0.408) | (0.501, -0.000, 0.420)→(0.497, 0.000, 0.448) | 0.340→0.368 | 0.00 / 0.000 | 0.000 | 0.000 |
| grasp_peg | grasp | 1.00 / step_budget | (0.500, -0.000, 0.408)→(0.498, -0.000, 0.400) | (0.497, 0.000, 0.448)→(0.496, 0.000, 0.440) | 0.368→0.360 | 0.00 / 0.000 | 0.000 | 0.000 |
| lift_peg | retract | 1.00 / step_budget | (0.498, -0.000, 0.400)→(0.497, -0.000, 0.418) | (0.496, 0.000, 0.440)→(0.493, 0.000, 0.458) | 0.360→0.378 | 0.00 / 0.000 | 0.000 | 0.000 |
| approach_hole | approach | 0.00 / step_budget | (0.497, -0.000, 0.418)→(0.502, 0.012, 0.219) | (0.493, 0.000, 0.458)→(0.510, 0.013, 0.258) | 0.378→0.180 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_hole | align | 1.00 / step_budget | (0.502, 0.012, 0.219)→(0.501, 0.015, 0.102) | (0.510, 0.013, 0.258)→(0.514, 0.015, 0.140) | 0.180→0.067 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_insert | descend | 0.33 / step_budget | (0.501, 0.015, 0.102)→(0.519, 0.011, 0.096) | (0.514, 0.015, 0.140)→(0.532, 0.011, 0.133) | 0.067→0.067 | 0.33 / 0.333 | 372.872 | 372.872 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.878
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.878
- phase_score: 0.433
- phase_breakdown.approach_hole_score: 0.151
- phase_breakdown.approach_peg_score: 0.828
- phase_breakdown.insert_task_score: 0.444

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.640
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.878
- **Median Q (composite search score)**: 0.040
- **K-run variance**: 0.0030
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.362


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `0c4288e4b4f4eb50f7d141bdaea44f8ed4eecfe7429f8148c247811f0f5250bc`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `2ae90e10c3e712e9da92b27bc0ded08b6d103e49e03139a26a0fa45d3ac81c97`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":20.0,"average_failure_rate":0.11429,"average_mean_iterations":25.84571,"average_solve_count":175.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.lateral_offset_x":-0.00072,"align_hole.lateral_offset_y":-0.00941,"approach_hole.speed":0.07817,"approach_peg.speed":0.05562,"descend_insert.force_threshold":16.55045,"descend_insert.insertion_depth":0.05512,"descend_to_peg.contact_force_threshold":7.68805,"descend_to_peg.descend_speed":0.04677,"lift_peg.lift_height":0.02465},"optimized_scores":{"best_composite_score":0.03556,"best_fitness_score":0.63556,"best_task_score":0.85812},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.0774,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.50509,0.02213,0.10152],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":962.0,"n_steps_budget":1000.0,"object_pos_end":[0.50103,-0.0,0.42112],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.34112,"object_to_goal_dist_start":0.26034,"object_z_max":0.42105,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_peg","tcp_end":[0.50236,-1e-05,0.38114],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.4965,1e-05,0.4528],"object_pos_start":[0.50103,-0.0,0.42112],"object_to_goal_dist_end":0.37282,"object_to_goal_dist_start":0.34112,"object_z_max":0.45274,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49999,-1e-05,0.41295],"tcp_start":[0.50236,-1e-05,0.38114],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4952,2e-05,0.44484],"object_pos_start":[0.4965,1e-05,0.4528],"object_to_goal_dist_end":0.36487,"object_to_goal_dist_start":0.37282,"object_z_max":0.45281,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49799,-2e-05,0.40493],"tcp_start":[0.49999,-1e-05,0.41295],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.49286,2e-05,0.46223],"object_pos_start":[0.4952,2e-05,0.44484],"object_to_goal_dist_end":0.38229,"object_to_goal_dist_start":0.36487,"object_z_max":0.46219,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49691,-3e-05,0.42243],"tcp_start":[0.49799,-2e-05,0.40493],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51154,0.02215,0.25222],"object_pos_start":[0.49286,2e-05,0.46223],"object_to_goal_dist_end":0.17402,"object_to_goal_dist_start":0.38229,"object_z_max":0.46223,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_hole","tcp_end":[0.50325,0.02205,0.21309],"tcp_start":[0.49691,-3e-05,0.42243],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":673.0,"n_steps_budget":720.0,"object_pos_end":[0.51715,0.0222,0.13966],"object_pos_start":[0.51154,0.02215,0.25222],"object_to_goal_dist_end":0.06592,"object_to_goal_dist_start":0.17402,"object_z_max":0.25222,"peak_contact_force":0.0,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50509,0.02213,0.10152],"tcp_start":[0.50325,0.02205,0.21309],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":0.0,"n_steps_budget":600.0,"object_pos_end":[0.51715,0.0222,0.13966],"object_pos_start":[0.51715,0.0222,0.13966],"object_to_goal_dist_end":0.06592,"object_to_goal_dist_start":0.06592,"peak_contact_force":0.0,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_task","tcp_end":[0.50509,0.02213,0.10152],"tcp_start":[0.50509,0.02213,0.10152],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `02e4649f08bda5439eae760bf0bc4b5a6b47c91c93317c6956c2509043be6196`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.32164,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.lateral_offset_x":-0.00059,"align_hole.lateral_offset_y":-0.00561,"approach_hole.speed":0.06226,"approach_peg.speed":0.05695,"descend_insert.force_threshold":20.64605,"descend_insert.insertion_depth":0.06235,"descend_to_peg.contact_force_threshold":7.72565,"descend_to_peg.descend_speed":0.04319,"lift_peg.lift_height":0.02447},"optimized_scores":{"best_composite_score":0.15382,"best_fitness_score":0.61096,"best_task_score":0.87779},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.54465,0.02032,0.0795],"force_p95":1118.61588,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1118.61588,"mean_force":1118.61588,"phase_index":6.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.53111,0.02123,0.0854]}],"total_contact_groups":1},"final_pose_error":0.08432,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.53429,0.02118,0.08455],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":1118.61588,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":932.0,"n_steps_budget":990.0,"object_pos_end":[0.50104,-0.0,0.42099],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.34099,"object_to_goal_dist_start":0.26034,"object_z_max":0.42092,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_peg","tcp_end":[0.50236,-1e-05,0.38101],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49651,1e-05,0.45267],"object_pos_start":[0.50104,-0.0,0.42099],"object_to_goal_dist_end":0.37269,"object_to_goal_dist_start":0.34099,"object_z_max":0.45262,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49999,-1e-05,0.41282],"tcp_start":[0.50236,-1e-05,0.38101],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49521,2e-05,0.44471],"object_pos_start":[0.49651,1e-05,0.45267],"object_to_goal_dist_end":0.36474,"object_to_goal_dist_start":0.37269,"object_z_max":0.45268,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49799,-2e-05,0.40481],"tcp_start":[0.49999,-1e-05,0.41282],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.49288,2e-05,0.46194],"object_pos_start":[0.49521,2e-05,0.44471],"object_to_goal_dist_end":0.38201,"object_to_goal_dist_start":0.36474,"object_z_max":0.46191,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49691,-3e-05,0.42215],"tcp_start":[0.49799,-2e-05,0.40481],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49611,0.02637,0.25882],"object_pos_start":[0.49288,2e-05,0.46194],"object_to_goal_dist_end":0.18079,"object_to_goal_dist_start":0.38201,"object_z_max":0.46194,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_hole","tcp_end":[0.48687,0.02617,0.2199],"tcp_start":[0.49691,-3e-05,0.42215],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":731.0,"n_steps_budget":780.0,"object_pos_end":[0.4957,0.03293,0.13924],"object_pos_start":[0.49611,0.02637,0.25882],"object_to_goal_dist_end":0.06791,"object_to_goal_dist_start":0.18079,"object_z_max":0.25882,"peak_contact_force":0.0,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.48182,0.0327,0.10172],"tcp_start":[0.48687,0.02617,0.2199],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":25.0,"n_steps_budget":600.0,"object_pos_end":[0.55163,0.01992,0.12057],"object_pos_start":[0.4957,0.03293,0.13924],"object_to_goal_dist_end":0.06862,"object_to_goal_dist_start":0.06791,"object_z_max":0.13924,"peak_contact_force":1118.61588,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":1118.61588,"subtask_id":"insert_task","tcp_end":[0.53429,0.02118,0.08455],"tcp_start":[0.48182,0.0327,0.10172],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7363bc0b3fa7329ef53220378736f8cf8ba8a5eef8ffe48ac32070ac53331cd4`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":20.0,"average_failure_rate":0.09479,"average_mean_iterations":21.59242,"average_solve_count":211.0,"average_success_count":191.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.lateral_offset_x":-0.00871,"align_hole.lateral_offset_y":0.00768,"approach_hole.speed":0.01309,"approach_peg.speed":0.09297,"descend_insert.force_threshold":29.99629,"descend_insert.insertion_depth":0.02442,"descend_to_peg.contact_force_threshold":9.40949,"descend_to_peg.descend_speed":0.01291,"lift_peg.lift_height":0.02559},"optimized_scores":{"best_composite_score":0.03997,"best_fitness_score":0.63997,"best_task_score":0.86981},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.04813,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.51672,-0.00949,0.10132],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":572.0,"n_steps_budget":630.0,"object_pos_end":[0.50111,-0.0,0.41929],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.33929,"object_to_goal_dist_start":0.26034,"object_z_max":0.41917,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_peg","tcp_end":[0.5023,-1e-05,0.3793],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49782,0.0,0.43867],"object_pos_start":[0.50111,-0.0,0.41929],"object_to_goal_dist_end":0.35868,"object_to_goal_dist_start":0.33929,"object_z_max":0.43865,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50028,-2e-05,0.39875],"tcp_start":[0.5023,-1e-05,0.3793],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49632,0.0,0.43063],"object_pos_start":[0.49782,0.0,0.43867],"object_to_goal_dist_end":0.35065,"object_to_goal_dist_start":0.35868,"object_z_max":0.43867,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49808,-3e-05,0.39067],"tcp_start":[0.50028,-2e-05,0.39875],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.49385,1e-05,0.4488],"object_pos_start":[0.49632,0.0,0.43063],"object_to_goal_dist_end":0.36885,"object_to_goal_dist_start":0.35065,"object_z_max":0.44877,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49688,-4e-05,0.40892],"tcp_start":[0.49808,-3e-05,0.39067],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52225,-0.01101,0.26229],"object_pos_start":[0.49385,1e-05,0.4488],"object_to_goal_dist_end":0.18397,"object_to_goal_dist_start":0.36885,"object_z_max":0.4488,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_hole","tcp_end":[0.51532,-0.01106,0.2229],"tcp_start":[0.49688,-4e-05,0.40892],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":732.0,"n_steps_budget":780.0,"object_pos_end":[0.52788,-0.00942,0.13973],"object_pos_start":[0.52225,-0.01101,0.26229],"object_to_goal_dist_end":0.06659,"object_to_goal_dist_start":0.18397,"object_z_max":0.26229,"peak_contact_force":0.0,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.51672,-0.00949,0.10132],"tcp_start":[0.51532,-0.01106,0.2229],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":0.0,"n_steps_budget":600.0,"object_pos_end":[0.52788,-0.00942,0.13973],"object_pos_start":[0.52788,-0.00942,0.13973],"object_to_goal_dist_end":0.06659,"object_to_goal_dist_start":0.06659,"peak_contact_force":0.0,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_task","tcp_end":[0.51672,-0.00949,0.10132],"tcp_start":[0.51672,-0.00949,0.10132],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```