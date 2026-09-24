## Search State

- **Seed**: 0
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.6757 | 0.65 | ❌ rejected |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.6280 | 0.69 | ✅ accepted |

**Proposal policy**: task_score is 0.65 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.676) — your mutation base

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

- **Composite score**: 0.676
- **task_score** (E): 0.649
- **fitness_score**: 0.686  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2204 |
| contact_1 | 1.00 | 1.00 | 0.0512 |
| push_1 | 1.00 | 1.00 | 0.1774 |
| retract_1 | 1.00 | 1.00 | 0.0893 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.124, 0.095) | (0.498, 0.080, 0.040)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.558 | 2.179 |
| contact_1 | contact | 1.00 / force_exceeded | (0.495, 0.124, 0.095)→(0.494, 0.110, 0.046) | (0.500, 0.081, 0.034)→(0.501, 0.079, 0.035) | 0.161→0.159 | 1.00 / 2.000 | 29.445 | 28.934 |
| push_1 | push | 1.00 / step_budget | (0.494, 0.110, 0.046)→(0.493, -0.067, 0.044) | (0.501, 0.079, 0.035)→(0.499, -0.039, 0.029) | 0.159→0.045 | 1.00 / 2.667 | 71.407 | 152.818 |
| retract_1 | retract | 1.00 / step_budget | (0.493, -0.067, 0.044)→(0.490, -0.067, 0.133) | (0.499, -0.039, 0.029)→(0.502, -0.039, 0.027) | 0.045→0.046 | 1.00 / 1.000 | 0.649 | 62.657 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.839
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.786
- phase_score: 0.922
- phase_breakdown.insertion_goal_score: 0.941
- phase_breakdown.pre_contact_score: 0.877

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.867
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.968
- **Median Q (composite search score)**: 0.678
- **K-run variance**: 0.0224
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.301


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41206,"average_solve_count":199.0,"average_success_count":199.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05134,"contact_1.contact_force":6.10229,"push_1.insertion_depth":0.19234,"push_1.push_speed":0.03505},"optimized_scores":{"best_composite_score":0.85746,"best_fitness_score":0.86746,"best_task_score":0.78596},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":408.0,"contact_point_centroid":[0.49798,-0.02281,0.04279],"force_p95":68.49631,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":74.71769,"mean_force":37.86647,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49943,-0.01183,0.04092]},{"body_a":"peg","body_b":"channel_base_body","contact_count":452.0,"contact_point_centroid":[0.49709,-0.03137,0.00933],"force_p95":66.13426,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":73.82199,"mean_force":32.28195,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49925,-0.00444,0.04074]},{"body_a":"attachment","body_b":"peg","contact_count":18.0,"contact_point_centroid":[0.49905,-0.09442,0.04356],"force_p95":41.49413,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":66.92927,"mean_force":6.65542,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50024,-0.08262,0.04296]},{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.50023,-0.0729,0.00815],"force_p95":0.69999,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":62.77282,"mean_force":0.91282,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49781,-0.0817,0.08582]},{"body_a":"peg","body_b":"channel_base_body","contact_count":119.0,"contact_point_centroid":[0.48075,-0.10044,0.02544],"force_p95":44.78948,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.99381,"mean_force":29.36823,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50068,-0.06366,0.04192]},{"body_a":"peg","body_b":"channel_base_body","contact_count":16.0,"contact_point_centroid":[0.47904,-0.10018,0.02562],"force_p95":10.55851,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.24479,"mean_force":2.89829,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5003,-0.08262,0.0428]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":19.0,"contact_point_centroid":[0.4749,-0.05032,0.02622],"force_p95":9.74728,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.55735,"mean_force":5.8364,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50002,-0.08265,0.04348]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":146.0,"contact_point_centroid":[0.47494,-0.04139,0.02667],"force_p95":16.91554,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.28314,"mean_force":10.94403,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50037,-0.04054,0.04171]},{"body_a":"peg","body_b":"channel_base_body","contact_count":287.0,"contact_point_centroid":[0.50396,0.06017,0.0094],"force_p95":0.55028,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.38603,"mean_force":0.62587,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50275,0.09849,0.07028]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50286,0.07909,0.05511],"force_p95":8.68997,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.13606,"mean_force":6.46028,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50083,0.0911,0.04586]},{"body_a":"peg","body_b":"channel_base_body","contact_count":674.0,"contact_point_centroid":[0.50367,0.0616,0.00935],"force_p95":0.58239,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55865,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50275,0.15189,0.19516]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52513,0.04289,0.03604],"force_p95":0.65895,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.74268,"mean_force":0.43108,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49737,0.07441,0.03866]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49977,0.19901,0.29841]}],"total_contact_groups":13},"final_pose_error":0.01146,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50464,-0.07271,0.02413],"final_tcp_position":[0.49784,-0.08165,0.13091],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":74.71769,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":697.0,"n_steps_budget":1000.0,"object_pos_end":[0.50376,0.06156,0.03378],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14175,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.54515,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":693.0,"raw_peak_contact_force":2.17216,"subtask_id":"pre_contact","tcp_end":[0.50702,0.10666,0.09871],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07912,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":287.0,"n_steps_budget":600.0,"object_pos_end":[0.50399,0.06082,0.03511],"object_pos_start":[0.50376,0.06156,0.03378],"object_to_goal_dist_end":0.14096,"object_to_goal_dist_start":0.14175,"object_z_max":0.03508,"peak_contact_force":9.38603,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":291.0,"raw_peak_contact_force":9.38603,"tcp_end":[0.50069,0.09033,0.04331],"tcp_start":[0.50702,0.10666,0.09871],"tcp_to_object_dist_end":0.03081,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":506.0,"n_steps_budget":1000.0,"object_pos_end":[0.4952,-0.07432,0.0261],"object_pos_start":[0.50399,0.06082,0.03511],"object_to_goal_dist_end":0.01577,"object_to_goal_dist_start":0.14096,"object_z_max":0.04027,"peak_contact_force":70.00347,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1141.0,"raw_peak_contact_force":74.71769,"subtask_id":"insertion_goal","tcp_end":[0.50081,-0.08218,0.04196],"tcp_start":[0.50069,0.09033,0.04331],"tcp_to_object_dist_end":0.01857,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.50464,-0.07271,0.02413],"object_pos_start":[0.4952,-0.07432,0.0261],"object_to_goal_dist_end":0.01807,"object_to_goal_dist_start":0.01577,"object_z_max":0.02679,"peak_contact_force":0.68341,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":596.0,"raw_peak_contact_force":66.92927,"tcp_end":[0.49784,-0.08165,0.13091],"tcp_start":[0.50081,-0.08218,0.04196],"tcp_to_object_dist_end":0.10737,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.33166,"average_solve_count":199.0,"average_success_count":199.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.03421,"contact_1.contact_force":6.79337,"push_1.insertion_depth":0.1987,"push_1.push_speed":0.03703},"optimized_scores":{"best_composite_score":0.67832,"best_fitness_score":0.68832,"best_task_score":0.96821},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":269.0,"contact_point_centroid":[0.49961,0.02616,0.04396],"force_p95":31.92919,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.51852,"mean_force":7.23605,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49321,0.037,0.03239]},{"body_a":"attachment","body_b":"peg","contact_count":60.0,"contact_point_centroid":[0.49815,-0.04766,0.05893],"force_p95":3.44691,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.24125,"mean_force":1.36324,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48983,-0.03707,0.04229]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":299.0,"contact_point_centroid":[0.5253,0.00378,0.03249],"force_p95":30.67721,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.45567,"mean_force":4.63109,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49318,0.03047,0.03237]},{"body_a":"peg","body_b":"channel_base_body","contact_count":201.0,"contact_point_centroid":[0.50549,0.02381,0.00962],"force_p95":18.09702,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.35061,"mean_force":5.11733,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49333,0.06578,0.03247]},{"body_a":"peg","body_b":"channel_base_body","contact_count":566.0,"contact_point_centroid":[0.50655,-0.06547,0.00952],"force_p95":0.59371,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.65794,"mean_force":0.5845,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48929,-0.03686,0.07656]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":85.0,"contact_point_centroid":[0.52518,-0.06246,0.02565],"force_p95":3.67095,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.27171,"mean_force":0.96112,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49036,-0.0373,0.03827]},{"body_a":"peg","body_b":"channel_base_body","contact_count":276.0,"contact_point_centroid":[0.5015,0.11237,0.00949],"force_p95":3.74799,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.21241,"mean_force":0.79236,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49589,0.15012,0.05928]},{"body_a":"attachment","body_b":"peg","contact_count":25.0,"contact_point_centroid":[0.49949,0.13225,0.05283],"force_p95":5.61168,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.0515,"mean_force":3.07559,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49638,0.14415,0.04116]},{"body_a":"peg","body_b":"channel_base_body","contact_count":654.0,"contact_point_centroid":[0.50093,0.11597,0.0094],"force_p95":0.61544,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55424,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49796,0.17823,0.18881]},{"body_a":"peg","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.51556,0.08568,0.06919],"force_p95":0.99727,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.66443,"mean_force":0.38917,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49303,0.11036,0.03172]}],"total_contact_groups":10},"final_pose_error":0.01085,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50659,-0.06203,0.03388],"final_tcp_position":[0.48941,-0.03682,0.12145],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":47.51852,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":670.0,"n_steps_budget":1000.0,"object_pos_end":[0.50099,0.11605,0.03382],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19615,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.58232,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":654.0,"raw_peak_contact_force":1.92055,"subtask_id":"pre_contact","tcp_end":[0.49758,0.15772,0.08329],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06477,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":282.0,"n_steps_budget":600.0,"object_pos_end":[0.50219,0.11328,0.03531],"object_pos_start":[0.50099,0.11605,0.03382],"object_to_goal_dist_end":0.19335,"object_to_goal_dist_start":0.19615,"object_z_max":0.03541,"peak_contact_force":8.74524,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":301.0,"raw_peak_contact_force":7.21241,"tcp_end":[0.49665,0.14273,0.03679],"tcp_start":[0.49758,0.15772,0.08329],"tcp_to_object_dist_end":0.03,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":479.0,"n_steps_budget":1000.0,"object_pos_end":[0.50823,-0.06243,0.03616],"object_pos_start":[0.50219,0.11328,0.03531],"object_to_goal_dist_end":0.01978,"object_to_goal_dist_start":0.19335,"object_z_max":0.042,"peak_contact_force":28.34265,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":783.0,"raw_peak_contact_force":47.51852,"subtask_id":"insertion_goal","tcp_end":[0.49238,-0.03714,0.03189],"tcp_start":[0.49665,0.14273,0.03679],"tcp_to_object_dist_end":0.03015,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.50659,-0.06203,0.03388],"object_pos_start":[0.50823,-0.06243,0.03616],"object_to_goal_dist_end":0.02009,"object_to_goal_dist_start":0.01978,"object_z_max":0.03685,"peak_contact_force":0.53723,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":711.0,"raw_peak_contact_force":38.24125,"tcp_end":[0.48941,-0.03682,0.12145],"tcp_start":[0.49238,-0.03714,0.03189],"tcp_to_object_dist_end":0.09274,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37624,"average_solve_count":202.0,"average_success_count":202.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05472,"contact_1.contact_force":4.85208,"push_1.insertion_depth":0.19953,"push_1.push_speed":0.03353},"optimized_scores":{"best_composite_score":0.49121,"best_fitness_score":0.50121,"best_task_score":0.19196},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":514.0,"contact_point_centroid":[0.475,-0.00073,0.05998],"force_p95":179.40183,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":336.21658,"mean_force":124.22752,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48568,0.00425,0.05849]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.475,-0.0852,0.05999],"force_p95":81.69907,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":82.80141,"mean_force":72.51286,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48666,-0.08302,0.05836]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47499,0.09014,0.05997],"force_p95":70.20383,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":70.20383,"mean_force":70.20383,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48483,0.0968,0.05853]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.48969,0.0793,0.05968],"force_p95":14.99578,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.16894,"mean_force":4.61287,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48527,0.09046,0.05854]},{"body_a":"peg","body_b":"channel_base_body","contact_count":733.0,"contact_point_centroid":[0.49466,0.02483,0.0084],"force_p95":0.74851,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.13344,"mean_force":0.7239,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48569,0.00559,0.05851]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":18.0,"contact_point_centroid":[0.47499,-0.00579,0.02415],"force_p95":10.03086,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.53553,"mean_force":3.91796,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48516,0.04885,0.05859]},{"body_a":"peg","body_b":"channel_base_body","contact_count":642.0,"contact_point_centroid":[0.49543,0.06381,0.00937],"force_p95":0.56779,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55881,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48839,0.15292,0.19682]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49934,0.1985,0.29704]},{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.49368,0.01829,0.00804],"force_p95":0.72553,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.81415,"mean_force":0.6059,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48385,-0.08239,0.10246]},{"body_a":"peg","body_b":"channel_base_body","contact_count":296.0,"contact_point_centroid":[0.49502,0.06381,0.0094],"force_p95":0.55046,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55289,"mean_force":0.54538,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48081,0.10262,0.07906]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.475,-0.00649,0.02415],"force_p95":0.36955,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36983,"mean_force":0.36702,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48363,-0.08228,0.11492]}],"total_contact_groups":11},"final_pose_error":0.01118,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49376,0.01845,0.0241],"final_tcp_position":[0.48386,-0.08233,0.14754],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":336.21658,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":669.0,"n_steps_budget":1000.0,"object_pos_end":[0.49525,0.06404,0.03396],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14424,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54591,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":670.0,"raw_peak_contact_force":2.44546,"subtask_id":"pre_contact","tcp_end":[0.47898,0.10912,0.10298],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08402,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":296.0,"n_steps_budget":600.0,"object_pos_end":[0.49535,0.06397,0.03401],"object_pos_start":[0.49525,0.06404,0.03396],"object_to_goal_dist_end":0.14417,"object_to_goal_dist_start":0.14424,"object_z_max":0.03401,"peak_contact_force":70.20383,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":297.0,"raw_peak_contact_force":70.20383,"tcp_end":[0.48486,0.09677,0.05841],"tcp_start":[0.47898,0.10912,0.10298],"tcp_to_object_dist_end":0.0422,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":746.0,"n_steps_budget":1000.0,"object_pos_end":[0.49487,0.01834,0.02415],"object_pos_start":[0.49535,0.06397,0.03401],"object_to_goal_dist_end":0.09974,"object_to_goal_dist_start":0.14417,"object_z_max":0.04077,"peak_contact_force":115.87429,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1272.0,"raw_peak_contact_force":336.21658,"subtask_id":"insertion_goal","tcp_end":[0.48666,-0.08288,0.05835],"tcp_start":[0.48486,0.09677,0.05841],"tcp_to_object_dist_end":0.10715,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.49376,0.01845,0.0241],"object_pos_start":[0.49487,0.01834,0.02415],"object_to_goal_dist_end":0.09992,"object_to_goal_dist_start":0.09974,"object_z_max":0.02425,"peak_contact_force":0.72588,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":548.0,"raw_peak_contact_force":82.80141,"tcp_end":[0.48386,-0.08233,0.14754],"tcp_start":[0.48666,-0.08288,0.05835],"tcp_to_object_dist_end":0.15966,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```