## Search State

- **Seed**: 7
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.3458 | 0.61 | ❌ rejected |
| 5 | approach → approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | 0.2605 | 0.66 | ✅ accepted |
| 4 | approach → contact → push | arc_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 9 | 0.1259 | 0.27 | ❌ rejected |
| 3 | approach → contact → push | arc_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.3374 | 0.57 | ✅ accepted |
| 2 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.3097 | 0.49 | ✅ accepted |

**Proposal policy**: task_score is 0.61 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`
- Frozen object start: [0.5100076373283734, 0.11177710407756605, 0.04]
- Frozen task target: [0.5100076373283734, -0.04822289592243395, 0.04]
- Goal object position: (0.5100076373283734, -0.04822289592243395, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5100076373283734, 0.11177710407756605, 0.04)
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
  frozen_object_start: [0.51, 0.1118, 0.04]
  frozen_task_target: [0.51, -0.0482, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5100076373283734, 0.11177710407756605, 0.04]}
  frozen_targets: {'channel_exit': [0.5100076373283734, -0.04822289592243395, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415

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

## Current Skill (Q=0.346) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
phases:
- id: align_to_entry
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - 0.1
    - 0.04
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.04
      - 0.12
      default: 0.08
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: generator.speed
        mode: replace
- id: approach_peg
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
    - 0.0
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: contact_peg
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
    - 0.01
    - 0.0
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 8.0
      default: 3.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact
- id: push_through
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
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.18
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_force_threshold:
      type: scalar
      range:
      - 10.0
      - 35.0
      default: 25.0
      binds_to:
      - path: guards.push_contact.threshold
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.025
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: push_contact
    when: during_phase
    predicate: force_below
    threshold: 25.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **align_to_entry** (`approach`)
  - target: source=yaml, anchor=world, offset=[0.5, 0.1, 0.04]
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.0]
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_peg** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.01, 0.0]
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_through** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_force_threshold: status=consumed; consumers=guards.push_contact.threshold (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=push_contact, when=during_phase, predicate=force_below, on_failure=retry, threshold=25.0
  - retries: max_attempts=2, strategy=reduce_speed

## Design Metrics

- **Composite score**: 0.346
- **task_score** (E): 0.612
- **fitness_score**: 0.639  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.460

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_to_entry | 0.67 | 1.00 | 0.2698 |
| approach_peg | 1.00 | 1.00 | 0.0244 |
| contact_peg | 0.67 | 1.00 | 0.0179 |
| push_through | 1.00 | 1.00 | 0.1762 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_to_entry | approach | 0.67 / step_budget | (0.500, 0.200, 0.300)→(0.496, 0.144, 0.037) | (0.509, 0.098, 0.040)→(0.503, 0.089, 0.035) | 0.179→0.169 | 1.00 / 1.667 | 5.543 | 15.496 |
| approach_peg | approach | 1.00 / step_budget | (0.496, 0.144, 0.037)→(0.499, 0.126, 0.031) | (0.503, 0.089, 0.035)→(0.503, 0.087, 0.035) | 0.169→0.167 | 1.00 / 1.333 | 0.514 | 12.615 |
| contact_peg | contact | 0.67 / force_exceeded | (0.499, 0.126, 0.031)→(0.496, 0.109, 0.029) | (0.503, 0.087, 0.035)→(0.504, 0.080, 0.035) | 0.167→0.160 | 1.00 / 2.333 | 1309.571 | 3.470 |
| push_through | push | 1.00 / step_budget | (0.496, 0.109, 0.029)→(0.499, -0.067, 0.028) | (0.504, 0.080, 0.035)→(0.506, -0.093, 0.036) | 0.160→0.015 | 1.00 / 3.000 | 88.959 | 150.069 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.996
- phase_score: 0.657
- phase_breakdown.approach_score: 0.535
- phase_breakdown.contact_score: 0.622
- phase_breakdown.push_score: 0.709

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.793
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.996
- **Median Q (composite search score)**: 0.340
- **K-run variance**: 0.0365
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.330


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `474e87cb3f7f98c9c8d99c8760356b7c026b70b97898f68d5a6c39ba94bca956`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a79e5fd8fc80d9ecadd30a274b12d8d7e7d0841df5ca68ae512c46dc86b114e6`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17416,"average_solve_count":178.0,"average_success_count":178.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_entry.arc_height":0.1209,"align_to_entry.speed":0.19999,"approach_peg.speed":0.13937,"contact_peg.contact_force":2.79267,"contact_peg.speed":0.04049,"push_through.push_distance":0.17959,"push_through.push_speed":0.03142,"push_through.push_tolerance":0.02645},"optimized_scores":{"best_composite_score":0.58257,"best_fitness_score":0.79257,"best_task_score":0.9961},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":60.0,"contact_point_centroid":[0.50581,-0.10363,0.04888],"force_p95":151.88901,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":155.48656,"mean_force":72.59177,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.5016,-0.06107,0.02825]},{"body_a":"attachment","body_b":"peg","contact_count":325.0,"contact_point_centroid":[0.50333,0.00838,0.04006],"force_p95":124.0535,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":155.38908,"mean_force":17.66946,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49931,0.01978,0.02684]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.535,0.09019,0.06],"force_p95":92.7895,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":102.74918,"mean_force":81.768,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49728,0.09028,0.02567]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":130.0,"contact_point_centroid":[0.52522,-0.01091,0.04253],"force_p95":28.48408,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.79718,"mean_force":8.14027,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49943,0.01842,0.02703]},{"body_a":"attachment","body_b":"peg","contact_count":28.0,"contact_point_centroid":[0.50385,0.10533,0.06017],"force_p95":7.9821,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.4412,"mean_force":5.02951,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49675,0.1167,0.03321]},{"body_a":"peg","body_b":"channel_base_body","contact_count":792.0,"contact_point_centroid":[0.50355,0.11083,0.00938],"force_p95":0.69897,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.85462,"mean_force":0.73483,"phase_index":0.0,"phase_name":"align_to_entry","phase_type":"approach","tcp_position_centroid":[0.49797,0.22696,0.14872]},{"body_a":"attachment","body_b":"peg","contact_count":24.0,"contact_point_centroid":[0.50156,0.12194,0.05156],"force_p95":18.48243,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.72984,"mean_force":5.84838,"phase_index":0.0,"phase_name":"align_to_entry","phase_type":"approach","tcp_position_centroid":[0.4966,0.13323,0.03373]},{"body_a":"peg","body_b":"channel_base_body","contact_count":58.0,"contact_point_centroid":[0.50608,0.08617,0.00964],"force_p95":2.3333,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.75971,"mean_force":1.18748,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49832,0.12068,0.03149]},{"body_a":"peg","body_b":"channel_base_body","contact_count":156.0,"contact_point_centroid":[0.50626,-0.01249,0.00981],"force_p95":23.8118,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.22933,"mean_force":6.00484,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49914,0.02747,0.02677]},{"body_a":"peg","body_b":"link7","contact_count":25.0,"contact_point_centroid":[0.52016,0.02836,0.06304],"force_p95":16.28785,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.53647,"mean_force":6.10767,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49816,0.05398,0.02592]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":42.0,"contact_point_centroid":[0.52555,0.08803,0.05864],"force_p95":8.18843,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.70195,"mean_force":2.74552,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49721,0.1179,0.03265]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":40.0,"contact_point_centroid":[0.5255,0.10264,0.03547],"force_p95":4.62661,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.57676,"mean_force":0.85649,"phase_index":0.0,"phase_name":"align_to_entry","phase_type":"approach","tcp_position_centroid":[0.49798,0.15571,0.13984]},{"body_a":"peg","body_b":"channel_base_body","contact_count":125.0,"contact_point_centroid":[0.50667,0.08405,0.00943],"force_p95":1.73258,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.48201,"mean_force":0.65479,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49848,0.11944,0.02812]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.50439,0.10463,0.05628],"force_p95":1.9395,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.01918,"mean_force":1.20647,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49813,0.11646,0.02719]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52506,0.08723,0.05881],"force_p95":0.0,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49993,0.12379,0.03059]}],"total_contact_groups":15},"final_pose_error":0.02633,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50493,-0.09472,0.03536],"final_tcp_position":[0.50135,-0.06833,0.02745],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":155.48656,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":841.0,"n_steps_budget":870.0,"object_pos_end":[0.50693,0.08943,0.03485],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.16965,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":15.14005,"phase_name":"align_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":856.0,"raw_peak_contact_force":33.85462,"tcp_end":[0.49664,0.11661,0.03414],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.02907,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":81.0,"n_steps_budget":600.0,"object_pos_end":[0.50688,0.0872,0.034],"object_pos_start":[0.50693,0.08943,0.03485],"object_to_goal_dist_end":0.16745,"object_to_goal_dist_start":0.16965,"object_z_max":0.0364,"peak_contact_force":0.56362,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":128.0,"raw_peak_contact_force":36.4412,"subtask_id":"approach","tcp_end":[0.49993,0.12371,0.03063],"tcp_start":[0.49664,0.11661,0.03414],"tcp_to_object_dist_end":0.03732,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":125.0,"n_steps_budget":600.0,"object_pos_end":[0.50681,0.08661,0.03492],"object_pos_start":[0.50688,0.0872,0.034],"object_to_goal_dist_end":0.16682,"object_to_goal_dist_start":0.16745,"object_z_max":0.0349,"peak_contact_force":7.33704,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":143.0,"raw_peak_contact_force":2.48201,"subtask_id":"contact","tcp_end":[0.49819,0.1157,0.02712],"tcp_start":[0.49993,0.12371,0.03063],"tcp_to_object_dist_end":0.03133,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":405.0,"n_steps_budget":1000.0,"object_pos_end":[0.50493,-0.09472,0.03536],"object_pos_start":[0.50681,0.08661,0.03492],"object_to_goal_dist_end":0.0162,"object_to_goal_dist_start":0.16682,"object_z_max":0.03795,"peak_contact_force":4.08334,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":719.0,"raw_peak_contact_force":155.48656,"subtask_id":"push","tcp_end":[0.50135,-0.06833,0.02745],"tcp_start":[0.49819,0.1157,0.02712],"tcp_to_object_dist_end":0.02778,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `3ca2e925d364d2c0fe81fb71ee31d40f947a20e349a0720e1c44a2dd2bc628da`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.22111,"average_solve_count":199.0,"average_success_count":199.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_entry.arc_height":0.11638,"align_to_entry.speed":0.13695,"approach_peg.speed":0.15376,"contact_peg.contact_force":4.84865,"contact_peg.speed":0.02927,"push_through.push_distance":0.17058,"push_through.push_speed":0.02956,"push_through.push_tolerance":0.01307},"optimized_scores":{"best_composite_score":0.11467,"best_fitness_score":0.57467,"best_task_score":0.45857},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":800.0,"contact_point_centroid":[0.49903,0.00069,0.0439],"force_p95":94.80682,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":103.01904,"mean_force":24.27047,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49114,0.01089,0.02917]},{"body_a":"peg","body_b":"channel_base_body","contact_count":206.0,"contact_point_centroid":[0.50764,-0.10127,0.06025],"force_p95":92.958,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":93.7491,"mean_force":70.05458,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49286,-0.05877,0.02963]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":756.0,"contact_point_centroid":[0.52523,-0.02142,0.0367],"force_p95":29.18495,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.9042,"mean_force":7.90806,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49124,0.00372,0.02916]},{"body_a":"peg","body_b":"channel_base_body","contact_count":601.0,"contact_point_centroid":[0.51068,-0.03138,0.00989],"force_p95":14.41698,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.91412,"mean_force":7.20021,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49124,0.00714,0.02919]},{"body_a":"peg","body_b":"link7","contact_count":83.0,"contact_point_centroid":[0.51975,0.07239,0.0636],"force_p95":13.13443,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.20994,"mean_force":5.49733,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48875,0.08759,0.02798]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.49615,0.11904,0.00943],"force_p95":0.61188,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.74922,"mean_force":0.57788,"phase_index":0.0,"phase_name":"align_to_entry","phase_type":"approach","tcp_position_centroid":[0.49774,0.2283,0.1512]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.49625,0.13559,0.03609],"force_p95":7.56381,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.27773,"mean_force":3.26619,"phase_index":0.0,"phase_name":"align_to_entry","phase_type":"approach","tcp_position_centroid":[0.4963,0.14739,0.03521]},{"body_a":"peg","body_b":"channel_base_body","contact_count":412.0,"contact_point_centroid":[0.49487,0.08641,0.00994],"force_p95":3.06977,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.26986,"mean_force":1.86831,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.4917,0.13217,0.03059]},{"body_a":"attachment","body_b":"peg","contact_count":402.0,"contact_point_centroid":[0.49445,0.11952,0.03993],"force_p95":2.75838,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.54897,"mean_force":1.55995,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49153,0.13135,0.03049]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"align_to_entry","phase_type":"approach","tcp_position_centroid":[0.50042,0.20015,0.29781]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.4959,0.09561,0.00991],"force_p95":0.78066,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.84975,"mean_force":0.53563,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49588,0.14353,0.03401]}],"total_contact_groups":11},"final_pose_error":0.0183,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50675,-0.08452,0.03589],"final_tcp_position":[0.4921,-0.06159,0.02872],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":103.01904,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49582,0.11372,0.03524],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19383,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.94136,"phase_name":"align_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1007.0,"raw_peak_contact_force":8.74922,"tcp_end":[0.49631,0.1441,0.03479],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.03039,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.49498,0.11088,0.03629],"object_pos_start":[0.49582,0.11372,0.03524],"object_to_goal_dist_end":0.19098,"object_to_goal_dist_start":0.19383,"object_z_max":0.03629,"peak_contact_force":0.4307,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20.0,"raw_peak_contact_force":0.84975,"subtask_id":"approach","tcp_end":[0.49523,0.14416,0.03322],"tcp_start":[0.49631,0.1441,0.03479],"tcp_to_object_dist_end":0.03343,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.49789,0.093,0.03546],"object_pos_start":[0.49498,0.11088,0.03629],"object_to_goal_dist_end":0.17307,"object_to_goal_dist_start":0.19098,"object_z_max":0.03629,"peak_contact_force":1.72393,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":814.0,"raw_peak_contact_force":4.26986,"subtask_id":"contact","tcp_end":[0.49118,0.12227,0.03139],"tcp_start":[0.49523,0.14416,0.03322],"tcp_to_object_dist_end":0.03031,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":978.0,"n_steps_budget":1000.0,"object_pos_end":[0.50675,-0.08452,0.03589],"object_pos_start":[0.49789,0.093,0.03546],"object_to_goal_dist_end":0.00911,"object_to_goal_dist_start":0.17307,"object_z_max":0.03746,"peak_contact_force":103.01904,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2446.0,"raw_peak_contact_force":103.01904,"subtask_id":"push","tcp_end":[0.4921,-0.06159,0.02872],"tcp_start":[0.49118,0.12227,0.03139],"tcp_to_object_dist_end":0.02814,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f85f1938a541e3d507519c8f918b8ca98f1f9baf6ab2f6f3ba2c32478e079e47`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.39683,"average_solve_count":189.0,"average_success_count":189.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_entry.arc_height":0.11403,"align_to_entry.speed":0.10293,"approach_peg.speed":0.11565,"contact_peg.contact_force":4.28726,"contact_peg.speed":0.02399,"push_through.push_distance":0.15858,"push_through.push_speed":0.03873,"push_through.push_tolerance":0.02837},"optimized_scores":{"best_composite_score":0.34009,"best_fitness_score":0.55009,"best_task_score":0.3816},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":125.0,"contact_point_centroid":[0.50626,-0.10529,0.04927],"force_p95":182.43084,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":191.70288,"mean_force":109.10826,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50232,-0.0663,0.02836]},{"body_a":"attachment","body_b":"peg","contact_count":327.0,"contact_point_centroid":[0.50474,-0.01983,0.0441],"force_p95":179.27476,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":191.34499,"mean_force":45.31634,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50071,-0.00879,0.02735]},{"body_a":"channel_base_body","body_b":"link7","contact_count":52.0,"contact_point_centroid":[0.57989,-0.10004,0.06495],"force_p95":149.92057,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":160.84541,"mean_force":87.50412,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50275,-0.07043,0.02824]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.53655,0.06366,0.06],"force_p95":94.78679,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":97.95594,"mean_force":83.10927,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.4987,0.0638,0.02582]},{"body_a":"peg","body_b":"channel_base_body","contact_count":133.0,"contact_point_centroid":[0.50758,-0.04664,0.00987],"force_p95":29.28126,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.69247,"mean_force":10.53595,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50057,-0.00683,0.02732]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":126.0,"contact_point_centroid":[0.5252,-0.00479,0.02941],"force_p95":23.96611,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.12057,"mean_force":4.41416,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49972,0.02423,0.02667]},{"body_a":"peg","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.51516,-0.04721,0.06589],"force_p95":16.15558,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.15272,"mean_force":8.08767,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50069,-0.01846,0.02756]},{"body_a":"peg","body_b":"channel_base_body","contact_count":972.0,"contact_point_centroid":[0.50586,0.06296,0.00937],"force_p95":0.55508,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56049,"phase_index":0.0,"phase_name":"align_to_entry","phase_type":"approach","tcp_position_centroid":[0.49774,0.23323,0.16653]},{"body_a":"peg","body_b":"channel_base_body","contact_count":462.0,"contact_point_centroid":[0.50599,0.05871,0.00949],"force_p95":2.18553,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.6573,"mean_force":0.85277,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49899,0.09806,0.02703]},{"body_a":"attachment","body_b":"peg","contact_count":106.0,"contact_point_centroid":[0.50384,0.07878,0.0422],"force_p95":2.87545,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.32438,"mean_force":1.54459,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49959,0.0906,0.02732]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"align_to_entry","phase_type":"approach","tcp_position_centroid":[0.50026,0.19997,0.29734]},{"body_a":"peg","body_b":"channel_base_body","contact_count":292.0,"contact_point_centroid":[0.50588,0.06298,0.00938],"force_p95":0.55276,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55532,"mean_force":0.54659,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.4974,0.1405,0.03462]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,0.06007,0.01057],"force_p95":0.36867,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36867,"mean_force":0.36867,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49985,0.08872,0.02753]}],"total_contact_groups":13},"final_pose_error":0.02849,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50535,-0.09848,0.03586],"final_tcp_position":[0.5036,-0.07195,0.02888],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":3919.65299,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.06297,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54709,"phase_name":"align_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1006.0,"raw_peak_contact_force":3.88411,"tcp_end":[0.49632,0.17189,0.04262],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10969,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":292.0,"n_steps_budget":600.0,"object_pos_end":[0.50595,0.06302,0.03381],"object_pos_start":[0.50593,0.06297,0.0338],"object_to_goal_dist_end":0.14328,"object_to_goal_dist_start":0.14323,"object_z_max":0.03381,"peak_contact_force":0.5468,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":292.0,"raw_peak_contact_force":0.55532,"subtask_id":"approach","tcp_end":[0.5009,0.11074,0.03008],"tcp_start":[0.49632,0.17189,0.04262],"tcp_to_object_dist_end":0.04813,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":469.0,"n_steps_budget":990.0,"object_pos_end":[0.50697,0.05913,0.03553],"object_pos_start":[0.50595,0.06302,0.03381],"object_to_goal_dist_end":0.13938,"object_to_goal_dist_start":0.14328,"object_z_max":0.03553,"peak_contact_force":3919.65299,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":569.0,"raw_peak_contact_force":3.6573,"subtask_id":"contact","tcp_end":[0.49987,0.08854,0.02755],"tcp_start":[0.5009,0.11074,0.03008],"tcp_to_object_dist_end":0.03129,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":394.0,"n_steps_budget":1000.0,"object_pos_end":[0.50535,-0.09848,0.03586],"object_pos_start":[0.50697,0.05913,0.03553],"object_to_goal_dist_end":0.01968,"object_to_goal_dist_start":0.13938,"object_z_max":0.03823,"peak_contact_force":159.77355,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":790.0,"raw_peak_contact_force":191.70288,"subtask_id":"push","tcp_end":[0.5036,-0.07195,0.02888],"tcp_start":[0.49987,0.08854,0.02755],"tcp_to_object_dist_end":0.02749,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```