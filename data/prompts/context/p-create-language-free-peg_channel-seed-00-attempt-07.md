## Search State

- **Seed**: 0
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.1421 | 0.06 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.6127 | 0.72 | ❌ rejected |
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.5229 | 0.40 | ❌ rejected |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.6309 | 0.78 | ✅ accepted |
| 3 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1747 | 0.56 | ❌ rejected |

**Proposal policy**: task_score is 0.06 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.142) — your mutation base

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

- **Composite score**: 0.142
- **task_score** (E): 0.055
- **fitness_score**: 0.202  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2170 |
| contact_1 | 1.00 | 1.00 | 0.0475 |
| push_1 | 0.00 | 1.00 | 0.0001 |
| retract_1 | 1.00 | 1.00 | 0.0889 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.125, 0.098) | (0.498, 0.080, 0.040)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.528 | 2.179 |
| contact_1 | contact | 1.00 / force_exceeded | (0.495, 0.125, 0.098)→(0.494, 0.096, 0.061) | (0.500, 0.080, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 2.000 | 13.487 | 13.209 |
| push_1 | push | 0.00 / guard_failure | (0.494, 0.078, 0.060)→(0.494, 0.078, 0.060) | (0.500, 0.080, 0.034)→(0.499, 0.071, 0.035) | 0.161→0.151 | 1.00 / 2.000 | 15.390 | 58.131 |
| retract_1 | retract | 1.00 / step_budget | (0.494, 0.078, 0.060)→(0.491, 0.078, 0.149) | (0.500, 0.071, 0.035)→(0.499, 0.071, 0.034) | 0.151→0.151 | 1.00 / 1.000 | 0.542 | 25.071 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.094
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.082
- phase_score: 0.310
- phase_breakdown.insertion_goal_score: 0.072
- phase_breakdown.pre_contact_score: 0.866

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.219
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.082
- **Median Q (composite search score)**: 0.147
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.339


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5641,"average_solve_count":117.0,"average_success_count":117.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.04926,"contact_1.contact_force":1.27547,"push_1.force_limit":59.96433,"push_1.insertion_depth":0.12053,"push_1.push_speed":0.03054},"optimized_scores":{"best_composite_score":0.15878,"best_fitness_score":0.21878,"best_task_score":0.08178},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":98.0,"contact_point_centroid":[0.50958,0.04111,0.0095],"force_p95":59.19675,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.97542,"mean_force":50.94852,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50135,0.06569,0.05986]},{"body_a":"attachment","body_b":"peg","contact_count":98.0,"contact_point_centroid":[0.51307,0.06656,0.05882],"force_p95":58.75281,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.5303,"mean_force":50.52243,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50135,0.06569,0.05986]},{"body_a":"peg","body_b":"channel_base_body","contact_count":573.0,"contact_point_centroid":[0.50294,0.04688,0.00942],"force_p95":0.56563,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.526,"mean_force":0.63244,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49866,0.04966,0.10372]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.51279,0.05212,0.05935],"force_p95":21.79275,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.0411,"mean_force":3.64849,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50125,0.04966,0.0605]},{"body_a":"peg","body_b":"channel_base_body","contact_count":678.0,"contact_point_centroid":[0.50361,0.0616,0.00935],"force_p95":0.58238,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55858,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50275,0.15185,0.19408]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49977,0.19902,0.29839]},{"body_a":"peg","body_b":"channel_base_body","contact_count":259.0,"contact_point_centroid":[0.50393,0.06162,0.00938],"force_p95":0.55557,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55781,"mean_force":0.54657,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50323,0.09242,0.0771]}],"total_contact_groups":7},"final_pose_error":0.01148,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50325,0.0466,0.03426],"final_tcp_position":[0.49874,0.04972,0.14899],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":59.97542,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":701.0,"n_steps_budget":1000.0,"object_pos_end":[0.50378,0.06161,0.03379],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14179,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.5536,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":697.0,"raw_peak_contact_force":2.17216,"subtask_id":"pre_contact","tcp_end":[0.50701,0.10665,0.09673],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07746,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":259.0,"n_steps_budget":600.0,"object_pos_end":[0.50376,0.06155,0.03379],"object_pos_start":[0.50378,0.06161,0.03379],"object_to_goal_dist_end":0.14174,"object_to_goal_dist_start":0.14179,"object_z_max":0.03379,"peak_contact_force":1.39258,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":259.0,"raw_peak_contact_force":0.55781,"tcp_end":[0.50165,0.07854,0.06051],"tcp_start":[0.50701,0.10665,0.09673],"tcp_to_object_dist_end":0.03174,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":98.0,"n_steps_budget":1000.0,"object_pos_end":[0.50358,0.04642,0.03503],"object_pos_start":[0.50376,0.06155,0.03379],"object_to_goal_dist_end":0.12657,"object_to_goal_dist_start":0.14174,"object_z_max":0.03504,"peak_contact_force":22.41857,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":196.0,"raw_peak_contact_force":59.97542,"subtask_id":"insertion_goal","tcp_end":[0.5018,0.05002,0.06004],"tcp_start":[0.50179,0.05017,0.06006],"tcp_to_object_dist_end":0.02533,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.50325,0.0466,0.03426],"object_pos_start":[0.50364,0.04618,0.03503],"object_to_goal_dist_end":0.12677,"object_to_goal_dist_start":0.12633,"object_z_max":0.03503,"peak_contact_force":0.54422,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":587.0,"raw_peak_contact_force":29.526,"tcp_end":[0.49874,0.04972,0.14899],"tcp_start":[0.5018,0.05002,0.06004],"tcp_to_object_dist_end":0.11485,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.216,"average_solve_count":125.0,"average_success_count":125.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.04923,"contact_1.contact_force":4.04517,"push_1.force_limit":58.95562,"push_1.insertion_depth":0.11966,"push_1.push_speed":0.02013},"optimized_scores":{"best_composite_score":0.14676,"best_fitness_score":0.20676,"best_task_score":0.07798},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":88.0,"contact_point_centroid":[0.50304,0.09661,0.00951],"force_p95":58.02961,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":63.57995,"mean_force":48.8565,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49531,0.12043,0.05971]},{"body_a":"attachment","body_b":"peg","contact_count":88.0,"contact_point_centroid":[0.5071,0.12114,0.05867],"force_p95":57.5844,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.07731,"mean_force":48.43192,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49531,0.12043,0.05971]},{"body_a":"peg","body_b":"channel_base_body","contact_count":544.0,"contact_point_centroid":[0.49984,0.10372,0.00942],"force_p95":0.592,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.73898,"mean_force":0.63525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49257,0.10643,0.10342]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.50678,0.10845,0.05916],"force_p95":21.3944,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.25705,"mean_force":3.52234,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49509,0.10672,0.06034]},{"body_a":"peg","body_b":"channel_base_body","contact_count":264.0,"contact_point_centroid":[0.50113,0.116,0.0094],"force_p95":0.62067,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.17463,"mean_force":0.62611,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49557,0.14391,0.07786]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.5076,0.13009,0.05876],"force_p95":21.7458,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.7458,"mean_force":21.7458,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49573,0.13046,0.0605]},{"body_a":"peg","body_b":"channel_base_body","contact_count":608.0,"contact_point_centroid":[0.50086,0.11598,0.0094],"force_p95":0.6148,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55496,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49802,0.17837,0.19651]}],"total_contact_groups":7},"final_pose_error":0.0118,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49989,0.10356,0.03405],"final_tcp_position":[0.49261,0.10649,0.1485],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":63.57995,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":624.0,"n_steps_budget":1000.0,"object_pos_end":[0.50097,0.11608,0.03379],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19618,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.48544,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":608.0,"raw_peak_contact_force":1.92055,"subtask_id":"pre_contact","tcp_end":[0.49768,0.15797,0.09846],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07713,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":264.0,"n_steps_budget":600.0,"object_pos_end":[0.50087,0.11602,0.03376],"object_pos_start":[0.50097,0.11608,0.03379],"object_to_goal_dist_end":0.19612,"object_to_goal_dist_start":0.19618,"object_z_max":0.03397,"peak_contact_force":22.17463,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":265.0,"raw_peak_contact_force":22.17463,"tcp_end":[0.49576,0.13036,0.06037],"tcp_start":[0.49768,0.15797,0.09846],"tcp_to_object_dist_end":0.03066,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":88.0,"n_steps_budget":1000.0,"object_pos_end":[0.50023,0.10356,0.03481],"object_pos_start":[0.50087,0.11602,0.03376],"object_to_goal_dist_end":0.18363,"object_to_goal_dist_start":0.19612,"object_z_max":0.03482,"peak_contact_force":22.78997,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":176.0,"raw_peak_contact_force":63.57995,"subtask_id":"insertion_goal","tcp_end":[0.4956,0.10711,0.05989],"tcp_start":[0.49558,0.10726,0.05991],"tcp_to_object_dist_end":0.02575,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":544.0,"n_steps_budget":630.0,"object_pos_end":[0.49989,0.10356,0.03405],"object_pos_start":[0.50032,0.10332,0.03481],"object_to_goal_dist_end":0.18366,"object_to_goal_dist_start":0.1834,"object_z_max":0.03481,"peak_contact_force":0.5382,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":558.0,"raw_peak_contact_force":29.73898,"tcp_end":[0.49261,0.10649,0.1485],"tcp_start":[0.4956,0.10711,0.05989],"tcp_to_object_dist_end":0.11472,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53922,"average_solve_count":102.0,"average_success_count":102.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05161,"contact_1.contact_force":3.5592,"push_1.force_limit":42.83797,"push_1.insertion_depth":0.13153,"push_1.push_speed":0.01937},"optimized_scores":{"best_composite_score":0.12079,"best_fitness_score":0.18079,"best_task_score":0.00559},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.48349,0.05288,0.00946],"force_p95":43.28612,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.83727,"mean_force":27.06704,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48341,0.07857,0.06019]},{"body_a":"attachment","body_b":"peg","contact_count":20.0,"contact_point_centroid":[0.49528,0.07835,0.05882],"force_p95":42.90968,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.54418,"mean_force":26.66282,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48341,0.07857,0.06019]},{"body_a":"peg","body_b":"channel_base_body","contact_count":304.0,"contact_point_centroid":[0.49489,0.06365,0.0094],"force_p95":0.55051,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.89371,"mean_force":0.59914,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48014,0.09416,0.07904]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49564,0.07992,0.05918],"force_p95":16.46901,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.46901,"mean_force":16.46901,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48377,0.07952,0.0609]},{"body_a":"peg","body_b":"channel_base_body","contact_count":545.0,"contact_point_centroid":[0.49425,0.06238,0.00941],"force_p95":0.56362,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.94885,"mean_force":0.59823,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48024,0.07664,0.10366]},{"body_a":"attachment","body_b":"peg","contact_count":13.0,"contact_point_centroid":[0.49452,0.07611,0.05878],"force_p95":9.90017,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.43473,"mean_force":2.23514,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48269,0.07689,0.06021]},{"body_a":"peg","body_b":"channel_base_body","contact_count":651.0,"contact_point_centroid":[0.49536,0.06398,0.00937],"force_p95":0.56718,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55863,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48837,0.15288,0.19527]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49935,0.19851,0.29703]}],"total_contact_groups":8},"final_pose_error":0.01149,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49424,0.06252,0.03403],"final_tcp_position":[0.48028,0.07667,0.14881],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":50.83727,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":678.0,"n_steps_budget":1000.0,"object_pos_end":[0.49487,0.06381,0.03396],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14403,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54597,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":679.0,"raw_peak_contact_force":2.44546,"subtask_id":"pre_contact","tcp_end":[0.47895,0.10903,0.09989],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08152,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":304.0,"n_steps_budget":600.0,"object_pos_end":[0.49512,0.06359,0.03401],"object_pos_start":[0.49487,0.06381,0.03396],"object_to_goal_dist_end":0.1438,"object_to_goal_dist_start":0.14403,"object_z_max":0.03401,"peak_contact_force":16.89371,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":305.0,"raw_peak_contact_force":16.89371,"tcp_end":[0.48381,0.07942,0.06078],"tcp_start":[0.47895,0.10903,0.09989],"tcp_to_object_dist_end":0.03309,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.49457,0.06276,0.03416],"object_pos_start":[0.49512,0.06359,0.03401],"object_to_goal_dist_end":0.14299,"object_to_goal_dist_start":0.1438,"object_z_max":0.03416,"peak_contact_force":0.961,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":40.0,"raw_peak_contact_force":50.83727,"subtask_id":"insertion_goal","tcp_end":[0.48324,0.07712,0.05991],"tcp_start":[0.48325,0.0772,0.05994],"tcp_to_object_dist_end":0.03158,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":545.0,"n_steps_budget":630.0,"object_pos_end":[0.49424,0.06252,0.03403],"object_pos_start":[0.49459,0.0626,0.03413],"object_to_goal_dist_end":0.14277,"object_to_goal_dist_start":0.14282,"object_z_max":0.03437,"peak_contact_force":0.54474,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":558.0,"raw_peak_contact_force":15.94885,"tcp_end":[0.48028,0.07667,0.14881],"tcp_start":[0.48324,0.07712,0.05991],"tcp_to_object_dist_end":0.11649,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```