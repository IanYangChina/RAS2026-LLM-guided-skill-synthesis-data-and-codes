## Search State

- **Seed**: 7
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | 0.1539 | 0.61 | ❌ rejected |
| 7 | approach → approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | -0.0616 | 0.00 | ❌ rejected |
| 6 | approach → approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.3458 | 0.61 | ❌ rejected |
| 5 | approach → approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | 0.2605 | 0.66 | ✅ accepted |
| 4 | approach → contact → push | arc_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 9 | 0.1259 | 0.27 | ❌ rejected |

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

## Current Skill (Q=0.154) — your mutation base

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

- **Composite score**: 0.154
- **task_score** (E): 0.606
- **fitness_score**: 0.581  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.083
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_to_entry | 1.00 | 1.00 | 0.2729 |
| approach_peg | 1.00 | 1.00 | 0.0066 |
| contact_peg | 0.33 | 1.00 | 0.0187 |
| push_through | 0.67 | 1.00 | 0.0982 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_to_entry | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.496, 0.123, 0.039) | (0.509, 0.098, 0.040)→(0.502, 0.086, 0.035) | 0.179→0.166 | 1.00 / 1.333 | 0.739 | 9.619 |
| approach_peg | approach | 1.00 / step_budget | (0.496, 0.123, 0.039)→(0.498, 0.123, 0.034) | (0.502, 0.086, 0.035)→(0.502, 0.085, 0.035) | 0.166→0.165 | 1.00 / 1.333 | 0.460 | 0.967 |
| contact_peg | contact | 0.33 / step_budget | (0.498, 0.123, 0.034)→(0.497, 0.105, 0.030) | (0.502, 0.085, 0.035)→(0.503, 0.075, 0.035) | 0.165→0.156 | 1.00 / 2.667 | 2.308 | 3.557 |
| push_through | push | 0.67 / step_budget | (0.497, 0.045, 0.030)→(0.499, -0.053, 0.030) | (0.503, 0.075, 0.035)→(0.507, -0.081, 0.036) | 0.156→0.008 | 1.00 / 2.667 | 11.456 | 24.937 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.411
- terminal_score: 0.453
- phase_score: 0.590
- phase_breakdown.approach_score: 0.555
- phase_breakdown.contact_score: 0.699
- phase_breakdown.push_score: 0.566

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.740
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.230
- **K-run variance**: 0.0199
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at lower bound**: push_through.push_tolerance
- **Final σ (mean)**: 0.303


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.32121,"average_solve_count":165.0,"average_success_count":165.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_entry.arc_height":0.09066,"align_to_entry.speed":0.13034,"approach_peg.speed":0.08812,"contact_peg.contact_force":5.97582,"contact_peg.speed":0.03526,"push_through.push_distance":0.14083,"push_through.push_force_threshold":32.33752,"push_through.push_speed":0.0419,"push_through.push_tolerance":0.01},"optimized_scores":{"best_composite_score":0.23036,"best_fitness_score":0.74036,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":791.0,"contact_point_centroid":[0.50474,0.01202,0.04346],"force_p95":8.47341,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.37538,"mean_force":3.35049,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50052,0.02385,0.02795]},{"body_a":"peg","body_b":"channel_base_body","contact_count":13.0,"contact_point_centroid":[0.50704,-0.10037,0.05639],"force_p95":24.65032,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.12788,"mean_force":16.01978,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50277,-0.0528,0.03019]},{"body_a":"peg","body_b":"channel_base_body","contact_count":943.0,"contact_point_centroid":[0.50373,0.11069,0.0094],"force_p95":0.61747,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.32028,"mean_force":0.69754,"phase_index":0.0,"phase_name":"align_to_entry","phase_type":"approach","tcp_position_centroid":[0.49768,0.20917,0.15472]},{"body_a":"attachment","body_b":"peg","contact_count":43.0,"contact_point_centroid":[0.50054,0.11983,0.05016],"force_p95":13.1346,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.75976,"mean_force":3.39801,"phase_index":0.0,"phase_name":"align_to_entry","phase_type":"approach","tcp_position_centroid":[0.49634,0.13122,0.04113]},{"body_a":"peg","body_b":"channel_base_body","contact_count":546.0,"contact_point_centroid":[0.50586,-0.02382,0.00994],"force_p95":8.55595,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.37455,"mean_force":4.74369,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50058,0.02282,0.02802]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":526.0,"contact_point_centroid":[0.52505,-0.00959,0.02359],"force_p95":2.79922,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.50265,"mean_force":0.7418,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50058,0.01965,0.028]},{"body_a":"peg","body_b":"channel_base_body","contact_count":403.0,"contact_point_centroid":[0.50668,0.07099,0.00988],"force_p95":3.51946,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.98067,"mean_force":2.07715,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49917,0.11581,0.02988]},{"body_a":"attachment","body_b":"peg","contact_count":370.0,"contact_point_centroid":[0.50368,0.10222,0.04212],"force_p95":3.4399,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.72852,"mean_force":2.08342,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49935,0.11395,0.02952]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":44.0,"contact_point_centroid":[0.52555,0.10403,0.03079],"force_p95":1.76615,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.81381,"mean_force":0.62062,"phase_index":0.0,"phase_name":"align_to_entry","phase_type":"approach","tcp_position_centroid":[0.49768,0.15417,0.13425]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":329.0,"contact_point_centroid":[0.52507,0.0835,0.02932],"force_p95":1.62558,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.11371,"mean_force":0.92527,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49965,0.11257,0.02944]},{"body_a":"peg","body_b":"channel_base_body","contact_count":70.0,"contact_point_centroid":[0.50671,0.08869,0.00968],"force_p95":1.12361,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.33104,"mean_force":0.55685,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49746,0.12362,0.03574]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52507,0.09607,0.04048],"force_p95":1.24346,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.29975,"mean_force":0.57994,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49777,0.12419,0.03595]},{"body_a":"attachment","body_b":"peg","contact_count":13.0,"contact_point_centroid":[0.50339,0.11343,0.05548],"force_p95":1.0188,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.25666,"mean_force":0.19503,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49808,0.12495,0.03511]}],"total_contact_groups":13},"final_pose_error":0.01305,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50701,-0.08308,0.03524],"final_tcp_position":[0.50276,-0.05354,0.03016],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":25.37538,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50669,0.09346,0.03677],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.17362,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.86661,"phase_name":"align_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1030.0,"raw_peak_contact_force":15.32028,"tcp_end":[0.4963,0.12116,0.03862],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.02964,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":72.0,"n_steps_budget":600.0,"object_pos_end":[0.50616,0.09415,0.03441],"object_pos_start":[0.50669,0.09346,0.03677],"object_to_goal_dist_end":0.17435,"object_to_goal_dist_start":0.17362,"object_z_max":0.03705,"peak_contact_force":0.37638,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":88.0,"raw_peak_contact_force":1.33104,"subtask_id":"approach","tcp_end":[0.49943,0.12738,0.03375],"tcp_start":[0.4963,0.12116,0.03862],"tcp_to_object_dist_end":0.03391,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":463.0,"n_steps_budget":600.0,"object_pos_end":[0.507,0.07605,0.03526],"object_pos_start":[0.50616,0.09415,0.03441],"object_to_goal_dist_end":0.15628,"object_to_goal_dist_start":0.17435,"object_z_max":0.03569,"peak_contact_force":1.88232,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1102.0,"raw_peak_contact_force":4.98067,"subtask_id":"contact","tcp_end":[0.50158,0.10569,0.02956],"tcp_start":[0.49943,0.12738,0.03375],"tcp_to_object_dist_end":0.03066,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50701,-0.08308,0.03524],"object_pos_start":[0.507,0.07605,0.03526],"object_to_goal_dist_end":0.00902,"object_to_goal_dist_start":0.15628,"object_z_max":0.0358,"peak_contact_force":25.37538,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1876.0,"raw_peak_contact_force":25.37538,"subtask_id":"push","tcp_end":[0.50276,-0.05354,0.03016],"tcp_start":[0.50158,0.10569,0.02956],"tcp_to_object_dist_end":0.03027,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.54264,"average_solve_count":129.0,"average_success_count":129.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_entry.arc_height":0.11149,"align_to_entry.speed":0.14434,"approach_peg.speed":0.16333,"contact_peg.contact_force":3.07798,"contact_peg.speed":0.03862,"push_through.push_distance":0.16331,"push_through.push_force_threshold":24.28963,"push_through.push_speed":0.06605,"push_through.push_tolerance":0.01345},"optimized_scores":{"best_composite_score":0.27535,"best_fitness_score":0.53535,"best_task_score":0.45321},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":495.0,"contact_point_centroid":[0.49585,0.01981,0.03762],"force_p95":16.34644,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.43607,"mean_force":4.71178,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48916,0.03025,0.02839]},{"body_a":"peg","body_b":"channel_base_body","contact_count":385.0,"contact_point_centroid":[0.50409,-0.00416,0.00986],"force_p95":13.24397,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.06462,"mean_force":4.94683,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48913,0.03608,0.0283]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.50693,-0.1002,0.05956],"force_p95":14.91082,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.19611,"mean_force":10.39026,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49025,-0.05474,0.03019]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":42.0,"contact_point_centroid":[0.47479,0.07621,0.0364],"force_p95":12.63808,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.70676,"mean_force":1.56741,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48866,0.10643,0.02722]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":373.0,"contact_point_centroid":[0.52514,-0.02625,0.02917],"force_p95":9.1802,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.1969,"mean_force":3.03241,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48943,-0.00192,0.02895]},{"body_a":"peg","body_b":"channel_base_body","contact_count":953.0,"contact_point_centroid":[0.49626,0.11855,0.00943],"force_p95":0.61869,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.65377,"mean_force":0.59553,"phase_index":0.0,"phase_name":"align_to_entry","phase_type":"approach","tcp_position_centroid":[0.49777,0.22378,0.14997]},{"body_a":"attachment","body_b":"peg","contact_count":28.0,"contact_point_centroid":[0.49678,0.12854,0.04502],"force_p95":7.65523,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.18868,"mean_force":1.72934,"phase_index":0.0,"phase_name":"align_to_entry","phase_type":"approach","tcp_position_centroid":[0.49632,0.14022,0.03614]},{"body_a":"peg","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.51945,0.03177,0.06337],"force_p95":4.28404,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.20753,"mean_force":0.91677,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48866,0.04739,0.02768]},{"body_a":"peg","body_b":"channel_base_body","contact_count":92.0,"contact_point_centroid":[0.49403,0.09052,0.00977],"force_p95":2.26314,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.2319,"mean_force":0.90924,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49253,0.12829,0.03124]},{"body_a":"attachment","body_b":"peg","contact_count":60.0,"contact_point_centroid":[0.49365,0.11596,0.03969],"force_p95":1.89204,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.88349,"mean_force":0.79846,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49218,0.12768,0.03091]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.49481,0.08451,0.00948],"force_p95":0.8912,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.0173,"mean_force":0.6867,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49582,0.13106,0.03428]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":29.0,"contact_point_centroid":[0.47324,0.11627,0.0277],"force_p95":0.76037,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.40967,"phase_index":0.0,"phase_name":"align_to_entry","phase_type":"approach","tcp_position_centroid":[0.49971,0.1887,0.25243]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":10.0,"contact_point_centroid":[0.47465,0.09574,0.05999],"force_p95":0.68151,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.75719,"mean_force":0.28787,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49548,0.13114,0.03388]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":6.0,"contact_point_centroid":[0.47481,0.09603,0.06],"force_p95":0.07464,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0756,"mean_force":0.06907,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49481,0.1318,0.0333]}],"total_contact_groups":14},"final_pose_error":0.01448,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50699,-0.08013,0.03666],"final_tcp_position":[0.4902,-0.05512,0.03014],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":29.43607,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49451,0.10064,0.03531],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.18079,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.80373,"phase_name":"align_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1010.0,"raw_peak_contact_force":9.65377,"tcp_end":[0.49635,0.13143,0.03502],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.03085,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.49285,0.09838,0.03591],"object_pos_start":[0.49451,0.10064,0.03531],"object_to_goal_dist_end":0.17857,"object_to_goal_dist_start":0.18079,"object_z_max":0.03589,"peak_contact_force":0.45586,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":30.0,"raw_peak_contact_force":1.0173,"subtask_id":"approach","tcp_end":[0.49503,0.13166,0.03349],"tcp_start":[0.49635,0.13143,0.03502],"tcp_to_object_dist_end":0.03344,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":92.0,"n_steps_budget":600.0,"object_pos_end":[0.4942,0.09514,0.03499],"object_pos_start":[0.49285,0.09838,0.03591],"object_to_goal_dist_end":0.17531,"object_to_goal_dist_start":0.17857,"object_z_max":0.03595,"peak_contact_force":3.2319,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":158.0,"raw_peak_contact_force":3.2319,"subtask_id":"contact","tcp_end":[0.49113,0.12492,0.03011],"tcp_start":[0.49503,0.13166,0.03349],"tcp_to_object_dist_end":0.03034,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":711.0,"n_steps_budget":1000.0,"object_pos_end":[0.50703,-0.07991,0.03663],"object_pos_start":[0.4942,0.09514,0.03499],"object_to_goal_dist_end":0.0078,"object_to_goal_dist_start":0.17531,"object_z_max":0.0373,"peak_contact_force":8.91975,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1322.0,"raw_peak_contact_force":29.43607,"subtask_id":"push","tcp_end":[0.4902,-0.05512,0.03014],"tcp_start":[0.49024,-0.05501,0.03017],"tcp_to_object_dist_end":0.03065,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.84585,"average_solve_count":253.0,"average_success_count":253.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_entry.arc_height":0.06435,"align_to_entry.speed":0.08246,"approach_peg.speed":0.11216,"contact_peg.contact_force":3.61312,"contact_peg.speed":0.0122,"push_through.push_distance":0.14065,"push_through.push_force_threshold":22.18169,"push_through.push_speed":0.02541,"push_through.push_tolerance":0.03529},"optimized_scores":{"best_composite_score":-0.04413,"best_fitness_score":0.46587,"best_task_score":0.36422},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":57.0,"contact_point_centroid":[0.50635,-0.01772,0.00984],"force_p95":10.89958,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.00012,"mean_force":4.7638,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49991,0.0268,0.02843]},{"body_a":"attachment","body_b":"peg","contact_count":169.0,"contact_point_centroid":[0.50378,0.015,0.0415],"force_p95":7.90676,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.45057,"mean_force":1.76983,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49977,0.02644,0.02823]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":101.0,"contact_point_centroid":[0.52517,-0.00535,0.03063],"force_p95":3.22233,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.88879,"mean_force":0.97513,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49991,0.02395,0.02834]},{"body_a":"peg","body_b":"channel_base_body","contact_count":972.0,"contact_point_centroid":[0.50586,0.06296,0.00937],"force_p95":0.55508,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56049,"phase_index":0.0,"phase_name":"align_to_entry","phase_type":"approach","tcp_position_centroid":[0.49749,0.19032,0.1554]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"align_to_entry","phase_type":"approach","tcp_position_centroid":[0.49996,0.19985,0.29632]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50683,0.05427,0.00962],"force_p95":1.63487,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.45754,"mean_force":0.89892,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49747,0.09442,0.03031]},{"body_a":"attachment","body_b":"peg","contact_count":420.0,"contact_point_centroid":[0.50319,0.07676,0.04362],"force_p95":1.98964,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.4536,"mean_force":1.17711,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49857,0.08848,0.02983]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":177.0,"contact_point_centroid":[0.52503,0.05698,0.03569],"force_p95":1.38744,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.61249,"mean_force":0.77305,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49906,0.08612,0.02971]},{"body_a":"peg","body_b":"channel_base_body","contact_count":49.0,"contact_point_centroid":[0.5062,0.06331,0.00938],"force_p95":0.55066,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55154,"mean_force":0.54663,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49676,0.11228,0.0389]}],"total_contact_groups":9},"final_pose_error":0.03524,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50647,-0.08144,0.03595],"final_tcp_position":[0.5027,-0.05098,0.0297],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":20.00012,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.06297,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54709,"phase_name":"align_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1006.0,"raw_peak_contact_force":3.88411,"tcp_end":[0.49629,0.11508,0.0422],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05366,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":49.0,"n_steps_budget":600.0,"object_pos_end":[0.50596,0.06294,0.03381],"object_pos_start":[0.50593,0.06297,0.0338],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14323,"object_z_max":0.03381,"peak_contact_force":0.54793,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":49.0,"raw_peak_contact_force":0.55154,"subtask_id":"approach","tcp_end":[0.49819,0.10904,0.0354],"tcp_start":[0.49629,0.11508,0.0422],"tcp_to_object_dist_end":0.04678,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50706,0.05519,0.03558],"object_pos_start":[0.50596,0.06294,0.03381],"object_to_goal_dist_end":0.13545,"object_to_goal_dist_start":0.1432,"object_z_max":0.03566,"peak_contact_force":1.80942,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1581.0,"raw_peak_contact_force":2.45754,"subtask_id":"contact","tcp_end":[0.49943,0.08436,0.02962],"tcp_start":[0.49819,0.10904,0.0354],"tcp_to_object_dist_end":0.03073,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":215.0,"n_steps_budget":1000.0,"object_pos_end":[0.50647,-0.08144,0.03595],"object_pos_start":[0.50706,0.05519,0.03558],"object_to_goal_dist_end":0.00777,"object_to_goal_dist_start":0.13545,"object_z_max":0.03873,"peak_contact_force":0.07344,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":327.0,"raw_peak_contact_force":20.00012,"subtask_id":"push","tcp_end":[0.5027,-0.05098,0.0297],"tcp_start":[0.49943,0.08436,0.02962],"tcp_to_object_dist_end":0.03132,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```