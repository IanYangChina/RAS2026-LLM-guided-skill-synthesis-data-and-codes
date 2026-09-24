## Search State

- **Seed**: 0
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.6127 | 0.72 | ❌ rejected |
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.5229 | 0.40 | ❌ rejected |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.6309 | 0.78 | ✅ accepted |
| 3 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1747 | 0.56 | ❌ rejected |
| 2 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1109 | 0.54 | ❌ rejected |

**Proposal policy**: task_score is 0.72 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454`
- Frozen object start: [0.5109569349857164, 0.061582937101109625, 0.04]
- Frozen task target: [0.5109569349857164, -0.09841706289889038, 0.04]
- Goal object position: (0.5109569349857164, -0.09841706289889038, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5109569349857164, 0.061582937101109625, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.2, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0.2, 0.3]
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
  frozen_object_start: [0.511, 0.0616, 0.04]
  frozen_task_target: [0.511, -0.0984, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5109569349857164, 0.061582937101109625, 0.04]}
  frozen_targets: {'channel_exit': [0.5109569349857164, -0.09841706289889038, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.781, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5109569349857164, 0.061582937101109625, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5109569349857164, -0.09841706289889038, 0.04) | final destination targets |
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

## Current Skill (Q=0.613) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.04
  - 0.06
  weight: 0.3
- id: insertion_goal
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.04
    - 0.06
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.03
      - 0.1
      default: 0.06
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: pre_contact
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.025
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 2.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: insertion_goal
- id: retract_1
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.06], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.025, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.613
- **task_score** (E): 0.723
- **fitness_score**: 0.706  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2055 |
| contact_1 | 0.67 | 1.00 | 0.0740 |
| push_1 | 1.00 | 1.00 | 0.1753 |
| retract_1 | 1.00 | 1.00 | 0.0892 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.125, 0.111) | (0.498, 0.080, 0.040)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.547 | 2.179 |
| contact_1 | contact | 0.67 / force_exceeded | (0.495, 0.125, 0.111)→(0.496, 0.108, 0.040) | (0.500, 0.081, 0.034)→(0.501, 0.078, 0.035) | 0.161→0.158 | 1.00 / 2.000 | 7.014 | 9.520 |
| push_1 | push | 1.00 / step_budget | (0.496, 0.108, 0.040)→(0.493, -0.067, 0.035) | (0.501, 0.078, 0.035)→(0.506, -0.070, 0.029) | 0.158→0.019 | 1.00 / 2.333 | 63.748 | 159.735 |
| retract_1 | retract | 1.00 / step_budget | (0.493, -0.067, 0.035)→(0.490, -0.067, 0.125) | (0.506, -0.070, 0.029)→(0.501, -0.070, 0.027) | 0.019→0.018 | 1.00 / 1.000 | 0.530 | 165.308 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.833
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.667
- phase_score: 0.909
- phase_breakdown.insertion_goal_score: 0.933
- phase_breakdown.pre_contact_score: 0.854

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.812
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.953
- **Median Q (composite search score)**: 0.708
- **K-run variance**: 0.0421
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.586


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `d6915c31707ac435a9367b840736087e39a7a48adfeb36a4f94b6b3ae57cce94`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `19172182883d287409b73cab43749e937e65f1ca1d4501d52b4a913a881aad36`; realized-scene SHA-256: `cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51096,0.06158,0.04]},{"name":"goal","value":[0.51096,-0.09842,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51096,0.06158,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51096,-0.09842,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.35266,"average_solve_count":207.0,"average_success_count":207.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.04788,"contact_1.contact_force":5.38612,"push_1.insertion_depth":0.1873,"push_1.push_speed":0.02072},"optimized_scores":{"best_composite_score":0.80236,"best_fitness_score":0.81236,"best_task_score":0.66683},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":410.0,"contact_point_centroid":[0.50385,-0.00492,0.04087],"force_p95":86.06219,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":94.57428,"mean_force":41.20106,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49847,0.00484,0.04097]},{"body_a":"peg","body_b":"channel_base_body","contact_count":446.0,"contact_point_centroid":[0.50572,-0.02139,0.00897],"force_p95":78.58124,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":82.25384,"mean_force":34.97304,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49862,0.00251,0.04113]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":254.0,"contact_point_centroid":[0.52521,-0.00398,0.03071],"force_p95":35.88279,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.09741,"mean_force":19.04667,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49824,0.02074,0.04085]},{"body_a":"peg","body_b":"channel_base_body","contact_count":546.0,"contact_point_centroid":[0.49747,-0.07081,0.00807],"force_p95":0.69709,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.24873,"mean_force":0.7044,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4959,-0.07643,0.08463]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":23.0,"contact_point_centroid":[0.47482,-0.09552,0.02434],"force_p95":10.63183,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.94582,"mean_force":2.77628,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49724,-0.07741,0.04398]},{"body_a":"peg","body_b":"channel_base_body","contact_count":276.0,"contact_point_centroid":[0.50378,0.06078,0.00938],"force_p95":0.55837,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.01701,"mean_force":0.61081,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50279,0.09872,0.06899]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.50306,0.07925,0.05719],"force_p95":8.69562,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.76613,"mean_force":3.81833,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50083,0.09128,0.04558]},{"body_a":"peg","body_b":"channel_base_body","contact_count":681.0,"contact_point_centroid":[0.50367,0.06159,0.00935],"force_p95":0.58246,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55851,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50274,0.15184,0.19339]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49978,0.19902,0.29839]}],"total_contact_groups":9},"final_pose_error":0.01142,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50151,-0.07171,0.02414],"final_tcp_position":[0.49599,-0.07633,0.12997],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":94.57428,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":704.0,"n_steps_budget":1000.0,"object_pos_end":[0.50375,0.06157,0.03378],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14175,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.55263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":700.0,"raw_peak_contact_force":2.17216,"subtask_id":"pre_contact","tcp_end":[0.507,0.10664,0.09543],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07644,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":276.0,"n_steps_budget":600.0,"object_pos_end":[0.50376,0.06112,0.03428],"object_pos_start":[0.50375,0.06157,0.03378],"object_to_goal_dist_end":0.14128,"object_to_goal_dist_start":0.14175,"object_z_max":0.03422,"peak_contact_force":10.01701,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":281.0,"raw_peak_contact_force":10.01701,"tcp_end":[0.50072,0.09077,0.04397],"tcp_start":[0.507,0.10664,0.09543],"tcp_to_object_dist_end":0.03134,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":502.0,"n_steps_budget":1000.0,"object_pos_end":[0.4968,-0.0708,0.02236],"object_pos_start":[0.50376,0.06112,0.03428],"object_to_goal_dist_end":0.02015,"object_to_goal_dist_start":0.14128,"object_z_max":0.04035,"peak_contact_force":0.54435,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1110.0,"raw_peak_contact_force":94.57428,"subtask_id":"insertion_goal","tcp_end":[0.49895,-0.07685,0.04098],"tcp_start":[0.50072,0.09077,0.04397],"tcp_to_object_dist_end":0.01969,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":546.0,"n_steps_budget":630.0,"object_pos_end":[0.50151,-0.07171,0.02414],"object_pos_start":[0.4968,-0.0708,0.02236],"object_to_goal_dist_end":0.01796,"object_to_goal_dist_start":0.02015,"object_z_max":0.02555,"peak_contact_force":0.52114,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":569.0,"raw_peak_contact_force":11.24873,"tcp_end":[0.49599,-0.07633,0.12997],"tcp_start":[0.49895,-0.07685,0.04098],"tcp_to_object_dist_end":0.10608,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `f24211f27d4adabdef509c8ed61621317fdbcaa86fc9ac888f85a717335bb714`; realized-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50095,0.11604,0.04]},{"name":"goal","value":[0.50095,-0.04396,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.11604,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50095,-0.04396,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34466,"average_solve_count":206.0,"average_success_count":206.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.04622,"contact_1.contact_force":9.02555,"push_1.insertion_depth":0.19952,"push_1.push_speed":0.01031},"optimized_scores":{"best_composite_score":0.70787,"best_fitness_score":0.71787,"best_task_score":0.95296},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":211.0,"contact_point_centroid":[0.50266,0.02748,0.00951],"force_p95":14.16002,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.56388,"mean_force":3.44175,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49343,0.06898,0.0349]},{"body_a":"attachment","body_b":"peg","contact_count":245.0,"contact_point_centroid":[0.49843,0.02722,0.04149],"force_p95":14.56534,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.94426,"mean_force":2.84129,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49338,0.03823,0.03491]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":156.0,"contact_point_centroid":[0.52522,-0.00754,0.02735],"force_p95":7.48344,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.8355,"mean_force":1.64947,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49335,0.01921,0.03491]},{"body_a":"peg","body_b":"channel_base_body","contact_count":311.0,"contact_point_centroid":[0.50133,0.1126,0.00947],"force_p95":3.04684,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.60879,"mean_force":0.85774,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49592,0.15026,0.06643]},{"body_a":"attachment","body_b":"peg","contact_count":25.0,"contact_point_centroid":[0.49895,0.13237,0.05139],"force_p95":7.74048,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.39801,"mean_force":4.23935,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49644,0.14429,0.04422]},{"body_a":"peg","body_b":"channel_base_body","contact_count":538.0,"contact_point_centroid":[0.50622,-0.06691,0.00942],"force_p95":0.62567,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.90228,"mean_force":0.5607,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49031,-0.0374,0.07943]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.49907,-0.04881,0.04382],"force_p95":5.20026,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.37548,"mean_force":1.07146,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49311,-0.03817,0.03495]},{"body_a":"peg","body_b":"channel_base_body","contact_count":616.0,"contact_point_centroid":[0.50094,0.11598,0.00937],"force_p95":0.62565,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55734,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49801,0.17833,0.19494]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":16.0,"contact_point_centroid":[0.47478,0.06264,0.05969],"force_p95":0.57005,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66401,"mean_force":0.17086,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49311,0.10929,0.03419]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":42.0,"contact_point_centroid":[0.52511,-0.06574,0.03302],"force_p95":0.5056,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54851,"mean_force":0.2467,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49145,-0.03809,0.04025]}],"total_contact_groups":10},"final_pose_error":0.01117,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50691,-0.06635,0.0338],"final_tcp_position":[0.49039,-0.03731,0.12415],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":21.56388,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":632.0,"n_steps_budget":1000.0,"object_pos_end":[0.50101,0.11612,0.03382],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19622,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.54639,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":616.0,"raw_peak_contact_force":1.92055,"subtask_id":"pre_contact","tcp_end":[0.49765,0.1579,0.09534],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07445,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":315.0,"n_steps_budget":600.0,"object_pos_end":[0.50137,0.11348,0.0349],"object_pos_start":[0.50101,0.11612,0.03382],"object_to_goal_dist_end":0.19355,"object_to_goal_dist_start":0.19622,"object_z_max":0.0355,"peak_contact_force":9.60879,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":336.0,"raw_peak_contact_force":9.60879,"tcp_end":[0.4967,0.14299,0.03924],"tcp_start":[0.49765,0.1579,0.09534],"tcp_to_object_dist_end":0.0302,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":476.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,-0.06352,0.03619],"object_pos_start":[0.50137,0.11348,0.0349],"object_to_goal_dist_end":0.01794,"object_to_goal_dist_start":0.19355,"object_z_max":0.04194,"peak_contact_force":8.95771,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":628.0,"raw_peak_contact_force":21.56388,"subtask_id":"insertion_goal","tcp_end":[0.49335,-0.03763,0.03492],"tcp_start":[0.4967,0.14299,0.03924],"tcp_to_object_dist_end":0.02883,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":545.0,"n_steps_budget":630.0,"object_pos_end":[0.50691,-0.06635,0.0338],"object_pos_start":[0.50597,-0.06352,0.03619],"object_to_goal_dist_end":0.0165,"object_to_goal_dist_start":0.01794,"object_z_max":0.03642,"peak_contact_force":0.54549,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":587.0,"raw_peak_contact_force":8.90228,"tcp_end":[0.49039,-0.03731,0.12415],"tcp_start":[0.49335,-0.03763,0.03492],"tcp_to_object_dist_end":0.09632,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `d098a7862ff18c9bbe982af3446a89a0fa6bcfa8790d7d955f65b2375d67a881`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41451,"average_solve_count":193.0,"average_success_count":193.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.0955,"contact_1.contact_force":9.56407,"push_1.insertion_depth":0.1984,"push_1.push_speed":0.03711},"optimized_scores":{"best_composite_score":0.32772,"best_fitness_score":0.58772,"best_task_score":0.5496},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":147.0,"contact_point_centroid":[0.47494,-0.08582,0.04412],"force_p95":382.21006,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":475.77413,"mean_force":234.43017,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48675,-0.0858,0.04229]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":33.0,"contact_point_centroid":[0.49209,-0.10019,0.065],"force_p95":342.7318,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":363.06752,"mean_force":257.01892,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48678,-0.08806,0.03039]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":6.0,"contact_point_centroid":[0.49215,-0.10008,0.065],"force_p95":299.73819,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":328.6191,"mean_force":148.65314,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48682,-0.0878,0.03041]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":553.0,"contact_point_centroid":[0.47499,-0.02678,0.03375],"force_p95":145.7805,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":278.17637,"mean_force":96.87273,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48684,-0.02677,0.03195]},{"body_a":"attachment","body_b":"peg","contact_count":884.0,"contact_point_centroid":[0.49668,-0.01942,0.03241],"force_p95":129.49104,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":139.43387,"mean_force":75.74005,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48688,-0.01574,0.03198]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":881.0,"contact_point_centroid":[0.52735,-0.02742,0.03035],"force_p95":119.35867,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":133.94949,"mean_force":69.55243,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48686,-0.01654,0.03195]},{"body_a":"attachment","body_b":"peg","contact_count":95.0,"contact_point_centroid":[0.49826,-0.0859,0.03433],"force_p95":111.42086,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":122.58467,"mean_force":59.45309,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48673,-0.08597,0.03568]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":112.0,"contact_point_centroid":[0.52822,-0.08624,0.02782],"force_p95":119.91914,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":122.25907,"mean_force":56.55499,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48674,-0.08585,0.03709]},{"body_a":"peg","body_b":"channel_base_body","contact_count":750.0,"contact_point_centroid":[0.51033,-0.02432,0.00959],"force_p95":76.95363,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":86.77947,"mean_force":41.47084,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48693,-0.00558,0.03218]},{"body_a":"peg","body_b":"link7","contact_count":582.0,"contact_point_centroid":[0.51638,-0.01715,0.06884],"force_p95":54.17282,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":61.71286,"mean_force":28.3249,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48686,-0.00424,0.03237]},{"body_a":"peg","body_b":"channel_base_body","contact_count":511.0,"contact_point_centroid":[0.49787,-0.07203,0.00835],"force_p95":27.95536,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.92019,"mean_force":3.38709,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48483,-0.08664,0.07655]},{"body_a":"peg","body_b":"channel_base_body","contact_count":80.0,"contact_point_centroid":[0.50761,-0.1001,0.02673],"force_p95":23.4296,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.88009,"mean_force":6.57592,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48683,-0.08222,0.03071]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":29.0,"contact_point_centroid":[0.47487,-0.06182,0.02493],"force_p95":11.12706,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.66786,"mean_force":3.56225,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48536,-0.08642,0.06337]},{"body_a":"peg","body_b":"channel_base_body","contact_count":624.0,"contact_point_centroid":[0.49578,0.06094,0.00945],"force_p95":0.70205,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.93423,"mean_force":0.71717,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4837,0.09961,0.08748]},{"body_a":"attachment","body_b":"peg","contact_count":43.0,"contact_point_centroid":[0.4928,0.0798,0.05622],"force_p95":7.08295,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.79636,"mean_force":2.77856,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48915,0.09159,0.04572]},{"body_a":"peg","body_b":"channel_base_body","contact_count":537.0,"contact_point_centroid":[0.49551,0.06382,0.00937],"force_p95":0.58406,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56139,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48863,0.15338,0.21715]}],"total_contact_groups":17},"final_pose_error":0.01123,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49448,-0.071,0.02405],"final_tcp_position":[0.48387,-0.08726,0.11956],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":475.77413,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":564.0,"n_steps_budget":1000.0,"object_pos_end":[0.49521,0.06405,0.03394],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14425,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54193,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":565.0,"raw_peak_contact_force":2.44546,"subtask_id":"pre_contact","tcp_end":[0.47943,0.11018,0.14292],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11939,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":631.0,"n_steps_budget":720.0,"object_pos_end":[0.49741,0.06031,0.03466],"object_pos_start":[0.49521,0.06405,0.03394],"object_to_goal_dist_end":0.14043,"object_to_goal_dist_start":0.14425,"object_z_max":0.0356,"peak_contact_force":1.41473,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":667.0,"raw_peak_contact_force":8.93423,"tcp_end":[0.49046,0.08967,0.03573],"tcp_start":[0.47943,0.11018,0.14292],"tcp_to_object_dist_end":0.03019,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":933.0,"n_steps_budget":1000.0,"object_pos_end":[0.51476,-0.07431,0.02859],"object_pos_start":[0.49741,0.06031,0.03466],"object_to_goal_dist_end":0.0195,"object_to_goal_dist_start":0.14043,"object_z_max":0.04012,"peak_contact_force":181.74256,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3763.0,"raw_peak_contact_force":363.06752,"subtask_id":"insertion_goal","tcp_end":[0.48683,-0.08789,0.03037],"tcp_start":[0.49046,0.08967,0.03573],"tcp_to_object_dist_end":0.03111,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.49448,-0.071,0.02405],"object_pos_start":[0.51476,-0.07431,0.02859],"object_to_goal_dist_end":0.01912,"object_to_goal_dist_start":0.0195,"object_z_max":0.02867,"peak_contact_force":0.52458,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":900.0,"raw_peak_contact_force":475.77413,"tcp_end":[0.48387,-0.08726,0.11956],"tcp_start":[0.48683,-0.08789,0.03037],"tcp_to_object_dist_end":0.09746,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```