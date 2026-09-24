## Search State

- **Seed**: 2
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | 0.2143 | 0.64 | ✅ accepted |
| 13 | align → approach → descend → contact → push → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 13 | -0.1970 | 0.41 | ✅ accepted |
| 12 | approach → descend → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.0063 | 0.30 | ❌ rejected |
| 11 | approach → descend → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.1405 | 0.11 | ❌ rejected |
| 10 | approach → descend → align → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.2463 | 0.22 | ❌ rejected |

**Proposal policy**: task_score is 0.64 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`
- Frozen object start: [0.48092897073994534, 0.06387929147312987, 0.04]
- Frozen task target: [0.48092897073994534, -0.09612070852687013, 0.04]
- Goal object position: (0.48092897073994534, -0.09612070852687013, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.48092897073994534, 0.06387929147312987, 0.04)
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
  frozen_object_start: [0.4809, 0.0639, 0.04]
  frozen_task_target: [0.4809, -0.0961, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.48092897073994534, 0.06387929147312987, 0.04]}
  frozen_targets: {'channel_exit': [0.48092897073994534, -0.09612070852687013, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach | object | (0.00, 0.04, 0.00) | distance | — |
| contact | object | (0.00, 0.02, 0.00) | distance | — |
| push | world | (0.50, -0.08, 0.04) | distance | push_depth |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.214) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.05
    - 0.12
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.08
      - 0.18
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    generator.speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.05
    - 0.005
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_z:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.005
      binds_to:
      - path: target.offset.z
        mode: replace
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
    - 0.005
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 1.0
      - 8.0
      default: 3.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_offset_y:
      type: scalar
      range:
      - -0.005
      - 0.015
      default: 0.005
      binds_to:
      - path: target.offset.y
        mode: replace
    generator.speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_force_check
    when: after_phase
    predicate: force_below
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.002
    - 0.0
  subtask_id: contact
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.14
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    generator.speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    push_depth:
      type: scalar
      range:
      - 0.05
      - 0.18
      default: 0.14
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  subtask_id: push
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.12], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - generator.speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.005], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_z: status=consumed; consumers=target.offset.z (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.005, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_offset_y: status=consumed; consumers=target.offset.y (replace)
    - generator.speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_force_check, when=after_phase, predicate=force_below, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.002, 0.0]
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.14, mode=add_to_offset, sign=positive}, tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - generator.speed: status=consumed; consumers=generator.speed (replace)
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.214
- **task_score** (E): 0.643
- **fitness_score**: 0.621  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.133
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.540

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1545 |
| descend_1 | 1.00 | 1.00 | 0.1146 |
| contact_1 | 1.00 | 1.00 | 0.0129 |
| push_1 | 1.00 | 1.00 | 0.1604 |
| retract_1 | 1.00 | 1.00 | 0.1010 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.493, 0.123, 0.169) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.547 | 3.659 |
| descend_1 | descend | 1.00 / step_budget | (0.493, 0.123, 0.169)→(0.494, 0.118, 0.057) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 1.000 | 0.545 | 185.910 |
| contact_1 | contact | 1.00 / force_exceeded | (0.493, 0.088, 0.037)→(0.495, 0.075, 0.038) | (0.498, 0.068, 0.034)→(0.499, 0.063, 0.035) | 0.148→0.143 | 1.00 / 2.667 | 15.926 | 21.782 |
| push_1 | push | 1.00 / step_budget | (0.495, 0.075, 0.038)→(0.504, -0.085, 0.034) | (0.503, 0.039, 0.035)→(0.497, -0.154, 0.020) | 0.120→0.098 | 1.00 / 3.000 | 173.540 | 323.305 |
| retract_1 | retract | 1.00 / step_budget | (0.504, -0.085, 0.034)→(0.502, -0.079, 0.135) | (0.497, -0.154, 0.020)→(0.509, -0.184, 0.017) | 0.098→0.136 | 1.00 / 1.000 | 0.613 | 76.188 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.792
- phase_score: 0.560
- phase_breakdown.approach_score: 0.055
- phase_breakdown.push_score: 0.765
- phase_breakdown.contact_score: 0.454

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.733
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.193
- **K-run variance**: 0.0054
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.412


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `6269840a353345700ffa70ea476a3ad730b138bf2ec3c52304c054f0e194e023`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a2936262b79fcd5a49fda15d77b54223f43c58bfee2e71dc505f8a2f79369706`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.27803,"average_solve_count":223.0,"average_success_count":223.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12573,"approach_1.generator.speed":0.21078,"contact_1.contact_force_threshold":3.8566,"contact_1.contact_offset_y":0.00387,"contact_1.generator.speed":0.0409,"descend_1.descend_z":0.0096,"push_1.generator.speed":0.04221,"push_1.push_depth":0.15225,"retract_1.retract_height":0.14977},"optimized_scores":{"best_composite_score":0.31325,"best_fitness_score":0.65325,"best_task_score":0.7924},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":181.0,"contact_point_centroid":[0.51342,-0.10023,0.065],"force_p95":296.31444,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":317.11318,"mean_force":224.42702,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50696,-0.08786,0.03158]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":84.0,"contact_point_centroid":[0.52509,-0.0881,0.05998],"force_p95":262.31545,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":263.39369,"mean_force":212.2073,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50737,-0.0874,0.03136]},{"body_a":"channel_base_body","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.54527,-0.1,0.06499],"force_p95":99.3117,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":215.99761,"mean_force":92.73687,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50724,-0.08728,0.03135]},{"body_a":"attachment","body_b":"peg","contact_count":240.0,"contact_point_centroid":[0.50208,-0.03706,0.03966],"force_p95":177.8494,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":197.4706,"mean_force":53.41075,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49973,-0.0257,0.02968]},{"body_a":"peg","body_b":"channel_base_body","contact_count":129.0,"contact_point_centroid":[0.49789,-0.10841,0.02687],"force_p95":190.86773,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":196.33978,"mean_force":88.89316,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50387,-0.07196,0.03137]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52506,-0.08797,0.05999],"force_p95":87.03284,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":102.39158,"mean_force":25.5979,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50724,-0.08719,0.03139]},{"body_a":"channel_base_body","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54535,-0.1,0.06498],"force_p95":68.33023,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":69.76271,"mean_force":51.87071,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50725,-0.08722,0.03136]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.51393,-0.10003,0.065],"force_p95":58.75898,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":59.35827,"mean_force":48.29687,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50725,-0.08722,0.03136]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":105.0,"contact_point_centroid":[0.52521,-0.00741,0.03408],"force_p95":39.07995,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.03797,"mean_force":9.51327,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49637,0.02094,0.02855]},{"body_a":"peg","body_b":"channel_base_body","contact_count":64.0,"contact_point_centroid":[0.50711,-0.04281,0.00975],"force_p95":33.27553,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.9397,"mean_force":8.24301,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49736,-0.0009,0.02867]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":39.0,"contact_point_centroid":[0.47489,-0.10493,0.05317],"force_p95":11.51641,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.02859,"mean_force":2.83854,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50459,-0.07626,0.03177]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1356.0,"contact_point_centroid":[0.50164,0.03292,0.00984],"force_p95":3.70061,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.31028,"mean_force":1.78736,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49023,0.07624,0.03379]},{"body_a":"attachment","body_b":"peg","contact_count":1108.0,"contact_point_centroid":[0.49676,0.0574,0.04263],"force_p95":3.61418,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.12374,"mean_force":1.85765,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49094,0.06877,0.03101]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":344.0,"contact_point_centroid":[0.52512,0.0263,0.0371],"force_p95":2.27481,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.41869,"mean_force":1.18809,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49473,0.05419,0.02967]},{"body_a":"peg","body_b":"world","contact_count":151.0,"contact_point_centroid":[0.47697,-0.1947,-0.00159],"force_p95":2.00034,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.41597,"mean_force":0.70521,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50709,-0.08759,0.03146]},{"body_a":"peg","body_b":"channel_base_body","contact_count":232.0,"contact_point_centroid":[0.49588,0.06414,0.00934],"force_p95":0.70021,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.58186,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.488,0.15156,0.24155]}],"total_contact_groups":19},"final_pose_error":0.02959,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49058,-0.32995,0.01415],"final_tcp_position":[0.50484,-0.08055,0.15241],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":317.11318,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":259.0,"n_steps_budget":600.0,"object_pos_end":[0.49493,0.06386,0.0339],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14408,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54345,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":260.0,"raw_peak_contact_force":2.44546,"subtask_id":"approach","tcp_end":[0.48066,0.12073,0.18443],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16155,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":434.0,"n_steps_budget":900.0,"object_pos_end":[0.49513,0.0641,0.03397],"object_pos_start":[0.49493,0.06386,0.0339],"object_to_goal_dist_end":0.14431,"object_to_goal_dist_start":0.14408,"object_z_max":0.03397,"peak_contact_force":0.54427,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":434.0,"raw_peak_contact_force":0.55295,"tcp_end":[0.49001,0.11369,0.05205],"tcp_start":[0.48066,0.12073,0.18443],"tcp_to_object_dist_end":0.05303,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1481.0,"n_steps_budget":780.0,"object_pos_end":[0.4956,0.06299,0.03508],"object_pos_start":[0.49513,0.0641,0.03397],"object_to_goal_dist_end":0.14314,"object_to_goal_dist_start":0.14431,"object_z_max":0.03644,"peak_contact_force":1.21277,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2808.0,"raw_peak_contact_force":8.31028,"subtask_id":"contact","tcp_end":[0.4972,0.04907,0.03077],"tcp_start":[0.49122,0.0701,0.03085],"tcp_to_object_dist_end":0.01466,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":484.0,"n_steps_budget":1000.0,"object_pos_end":[0.47464,-0.23022,0.01416],"object_pos_start":[0.5072,0.02043,0.03587],"object_to_goal_dist_end":0.15453,"object_to_goal_dist_start":0.10077,"object_z_max":0.0437,"peak_contact_force":195.90215,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1015.0,"raw_peak_contact_force":317.11318,"subtask_id":"push","tcp_end":[0.50725,-0.08725,0.03136],"tcp_start":[0.4972,0.04907,0.03077],"tcp_to_object_dist_end":0.14765,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":236.0,"n_steps_budget":930.0,"object_pos_end":[0.49058,-0.32995,0.01415],"object_pos_start":[0.47464,-0.23022,0.01416],"object_to_goal_dist_end":0.25146,"object_to_goal_dist_start":0.15453,"object_z_max":0.01417,"peak_contact_force":0.61442,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":246.0,"raw_peak_contact_force":102.39158,"tcp_end":[0.50484,-0.08055,0.15241],"tcp_start":[0.50725,-0.08725,0.03136],"tcp_to_object_dist_end":0.28552,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `78f29ebb38dd2df9149fb0cd7c7c33d55e802bb94eee599b284bb0b197a04fb7`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36869,"average_solve_count":198.0,"average_success_count":198.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.0902,"approach_1.generator.speed":0.2092,"contact_1.contact_force_threshold":3.22475,"contact_1.contact_offset_y":0.00527,"contact_1.generator.speed":0.06127,"descend_1.descend_z":0.00646,"push_1.generator.speed":0.02876,"push_1.push_depth":0.168,"retract_1.retract_height":0.1325},"optimized_scores":{"best_composite_score":0.13677,"best_fitness_score":0.47677,"best_task_score":0.13592},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":57.0,"contact_point_centroid":[0.47496,0.10757,0.05974],"force_p95":491.24573,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":556.62682,"mean_force":378.97198,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48608,0.10916,0.05772]},{"body_a":"peg","body_b":"channel_base_body","contact_count":365.0,"contact_point_centroid":[0.5004,-0.00213,0.00848],"force_p95":129.64448,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":132.60692,"mean_force":65.67712,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49086,0.01491,0.04356]},{"body_a":"attachment","body_b":"peg","contact_count":276.0,"contact_point_centroid":[0.49972,-0.00252,0.0424],"force_p95":129.97453,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":132.02706,"mean_force":86.20799,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49179,-0.00092,0.04243]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47497,0.10038,0.05256],"force_p95":105.20822,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":111.16793,"mean_force":73.11275,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48676,0.10036,0.05049]},{"body_a":"attachment","body_b":"peg","contact_count":19.0,"contact_point_centroid":[0.50189,-0.07034,0.04246],"force_p95":52.49273,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.73432,"mean_force":11.02895,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49781,-0.0811,0.04189]},{"body_a":"peg","body_b":"channel_base_body","contact_count":202.0,"contact_point_centroid":[0.50175,-0.04291,0.00843],"force_p95":5.04234,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":52.45865,"mean_force":1.69987,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49659,-0.07256,0.08944]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47497,0.10801,0.05417],"force_p95":49.62695,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":50.06702,"mean_force":37.13269,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48675,0.108,0.0521]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":13.0,"contact_point_centroid":[0.52508,-0.06006,0.02429],"force_p95":6.01099,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.19425,"mean_force":2.02489,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49637,-0.07059,0.07924]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":11.0,"contact_point_centroid":[0.47479,-0.02541,0.0388],"force_p95":3.73708,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.04768,"mean_force":1.21411,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49705,-0.07991,0.04569]},{"body_a":"peg","body_b":"channel_base_body","contact_count":284.0,"contact_point_centroid":[0.49448,0.05894,0.00932],"force_p95":0.64373,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.59769,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47897,0.14578,0.22357]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49759,0.19474,0.29441]},{"body_a":"peg","body_b":"channel_base_body","contact_count":390.0,"contact_point_centroid":[0.49419,0.05885,0.00939],"force_p95":0.55036,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55326,"mean_force":0.54619,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47661,0.11081,0.09548]},{"body_a":"peg","body_b":"channel_base_body","contact_count":14.0,"contact_point_centroid":[0.4916,0.06167,0.00939],"force_p95":0.5501,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55044,"mean_force":0.54639,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48718,0.10861,0.05296]}],"total_contact_groups":13},"final_pose_error":0.02969,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50193,-0.0389,0.02409],"final_tcp_position":[0.49657,-0.07403,0.14338],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":556.62682,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":313.0,"n_steps_budget":600.0,"object_pos_end":[0.49416,0.05887,0.03384],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13913,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54766,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":319.0,"raw_peak_contact_force":4.20518,"subtask_id":"approach","tcp_end":[0.46665,0.11361,0.1495],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13088,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":390.0,"n_steps_budget":720.0,"object_pos_end":[0.49427,0.05895,0.03389],"object_pos_start":[0.49416,0.05887,0.03384],"object_to_goal_dist_end":0.1392,"object_to_goal_dist_start":0.13913,"object_z_max":0.03389,"peak_contact_force":0.54693,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":447.0,"raw_peak_contact_force":556.62682,"tcp_end":[0.48787,0.10919,0.0544],"tcp_start":[0.46665,0.11361,0.1495],"tcp_to_object_dist_end":0.05464,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":14.0,"n_steps_budget":600.0,"object_pos_end":[0.49408,0.05882,0.03389],"object_pos_start":[0.49427,0.05895,0.03389],"object_to_goal_dist_end":0.13908,"object_to_goal_dist_start":0.1392,"object_z_max":0.03389,"peak_contact_force":45.66641,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":17.0,"raw_peak_contact_force":50.06702,"subtask_id":"contact","tcp_end":[0.4867,0.10785,0.05192],"tcp_start":[0.48672,0.10791,0.052],"tcp_to_object_dist_end":0.05275,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":367.0,"n_steps_budget":1000.0,"object_pos_end":[0.50034,-0.04796,0.03292],"object_pos_start":[0.49418,0.05882,0.03389],"object_to_goal_dist_end":0.03282,"object_to_goal_dist_start":0.13908,"object_z_max":0.03994,"peak_contact_force":98.98575,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":669.0,"raw_peak_contact_force":132.60692,"subtask_id":"push","tcp_end":[0.49895,-0.08034,0.0398],"tcp_start":[0.4867,0.10785,0.05192],"tcp_to_object_dist_end":0.03313,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":202.0,"n_steps_budget":840.0,"object_pos_end":[0.50193,-0.0389,0.02409],"object_pos_start":[0.50034,-0.04796,0.03292],"object_to_goal_dist_end":0.04411,"object_to_goal_dist_start":0.03282,"object_z_max":0.03364,"peak_contact_force":0.49871,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":245.0,"raw_peak_contact_force":52.73432,"tcp_end":[0.49657,-0.07403,0.14338],"tcp_start":[0.49895,-0.08034,0.0398],"tcp_to_object_dist_end":0.12447,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ecba62e37d233197bb248f7fe6e722b45204af5e83240a6f27138a89bcccfe42`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.96708,"average_solve_count":243.0,"average_success_count":243.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1151,"approach_1.generator.speed":0.22019,"contact_1.contact_force_threshold":6.25073,"contact_1.contact_offset_y":0.01042,"contact_1.generator.speed":0.01912,"descend_1.descend_z":0.01976,"push_1.generator.speed":0.04482,"push_1.push_depth":0.17105,"retract_1.retract_height":0.10682},"optimized_scores":{"best_composite_score":0.19302,"best_fitness_score":0.73302,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":186.0,"contact_point_centroid":[0.51257,-0.10015,0.065],"force_p95":457.01003,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":520.1942,"mean_force":272.18809,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50593,-0.08772,0.0312]},{"body_a":"channel_base_body","body_b":"link7","contact_count":174.0,"contact_point_centroid":[0.54329,-0.1,0.06496],"force_p95":367.84907,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":426.01332,"mean_force":225.15815,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50595,-0.08757,0.0312]},{"body_a":"attachment","body_b":"peg","contact_count":227.0,"contact_point_centroid":[0.50431,-0.02485,0.03876],"force_p95":154.99223,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":209.79403,"mean_force":32.7764,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50188,-0.01331,0.02861]},{"body_a":"peg","body_b":"channel_base_body","contact_count":119.0,"contact_point_centroid":[0.50115,-0.10873,0.03338],"force_p95":174.70655,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":206.56277,"mean_force":58.33526,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50376,-0.07231,0.02983]},{"body_a":"channel_base_body","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54419,-0.1,0.06495],"force_p95":73.22251,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":73.43949,"mean_force":59.409,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50622,-0.08721,0.03137]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.51297,-0.10003,0.065],"force_p95":51.42146,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":53.24775,"mean_force":29.41088,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50622,-0.08721,0.03137]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":89.0,"contact_point_centroid":[0.52518,-0.01803,0.03276],"force_p95":31.74733,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":52.63736,"mean_force":5.73131,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50148,0.01171,0.02842]},{"body_a":"peg","body_b":"channel_base_body","contact_count":78.0,"contact_point_centroid":[0.50023,-0.04431,0.00972],"force_p95":21.19439,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.65194,"mean_force":5.91787,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50174,-0.00281,0.02855]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":8.0,"contact_point_centroid":[0.47473,-0.10317,0.0589],"force_p95":12.36936,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.36751,"mean_force":5.68176,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50398,-0.07482,0.02999]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2074.0,"contact_point_centroid":[0.50645,0.04923,0.00986],"force_p95":3.00551,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.96836,"mean_force":1.54683,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5011,0.09416,0.03561]},{"body_a":"attachment","body_b":"peg","contact_count":1701.0,"contact_point_centroid":[0.50399,0.0764,0.03986],"force_p95":2.81273,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.66191,"mean_force":1.53798,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50081,0.08823,0.03208]},{"body_a":"peg","body_b":"channel_base_body","contact_count":240.0,"contact_point_centroid":[0.5053,0.08093,0.00933],"force_p95":0.64496,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.61035,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51906,0.15912,0.23534]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50185,0.19546,0.29448]},{"body_a":"peg","body_b":"world","contact_count":152.0,"contact_point_centroid":[0.50753,-0.17949,-0.00166],"force_p95":1.74321,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.22324,"mean_force":0.68793,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50599,-0.08752,0.03122]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":715.0,"contact_point_centroid":[0.52503,0.0468,0.03323],"force_p95":1.1041,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.83402,"mean_force":0.53693,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50047,0.07622,0.02861]},{"body_a":"peg","body_b":"link7","contact_count":13.0,"contact_point_centroid":[0.52182,-0.02817,0.06489],"force_p95":0.60637,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.76213,"mean_force":0.15322,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50107,-0.00121,0.02774]}],"total_contact_groups":18},"final_pose_error":0.02984,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.53369,-0.18288,0.01407],"final_tcp_position":[0.50358,-0.08161,0.109],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":3920.69488,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":269.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.55056,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":276.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach","tcp_end":[0.53069,0.13506,0.17381],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15217,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":325.0,"n_steps_budget":780.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":0.54459,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":325.0,"raw_peak_contact_force":0.55048,"tcp_end":[0.50554,0.1305,0.0634],"tcp_start":[0.53069,0.13506,0.17381],"tcp_to_object_dist_end":0.0578,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":2156.0,"n_steps_budget":1000.0,"object_pos_end":[0.50649,0.06604,0.03529],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.14626,"object_to_goal_dist_start":0.1611,"object_z_max":0.03576,"peak_contact_force":0.89954,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4490.0,"raw_peak_contact_force":6.96836,"subtask_id":"contact","tcp_end":[0.50254,0.06837,0.0304],"tcp_start":[0.50068,0.08484,0.02948],"tcp_to_object_dist_end":0.00671,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":494.0,"n_steps_budget":1000.0,"object_pos_end":[0.51587,-0.18359,0.01408],"object_pos_start":[0.50705,0.0386,0.03539],"object_to_goal_dist_end":0.10796,"object_to_goal_dist_start":0.1189,"object_z_max":0.04048,"peak_contact_force":225.73315,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1046.0,"raw_peak_contact_force":520.1942,"subtask_id":"push","tcp_end":[0.50622,-0.08724,0.03136],"tcp_start":[0.50254,0.06837,0.0304],"tcp_to_object_dist_end":0.09836,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":153.0,"n_steps_budget":690.0,"object_pos_end":[0.53369,-0.18288,0.01407],"object_pos_start":[0.51587,-0.18359,0.01408],"object_to_goal_dist_end":0.11132,"object_to_goal_dist_start":0.10796,"object_z_max":0.01409,"peak_contact_force":0.72601,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":159.0,"raw_peak_contact_force":73.43949,"tcp_end":[0.50358,-0.08161,0.109],"tcp_start":[0.50622,-0.08724,0.03136],"tcp_to_object_dist_end":0.14204,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```