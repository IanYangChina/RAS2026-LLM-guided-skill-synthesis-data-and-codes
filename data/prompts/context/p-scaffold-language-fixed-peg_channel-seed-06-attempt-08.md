## Search State

- **Seed**: 6
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → approach → contact → push → retract → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3271 | 0.67 | ❌ rejected |
| 7 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.4891 | 0.74 | ✅ accepted |
| 6 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.1237 | 0.01 | ❌ rejected |
| 5 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.4079 | 0.57 | ❌ rejected |
| 4 | approach → align → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.3377 | 0.19 | ❌ rejected |

**Proposal policy**: task_score is 0.67 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`
- Frozen object start: [0.5030531481177555, 0.06746166958506708, 0.04]
- Frozen task target: [0.5030531481177555, -0.09253833041493292, 0.04]
- Goal object position: (0.5030531481177555, -0.09253833041493292, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5030531481177555, 0.06746166958506708, 0.04)
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
  frozen_object_start: [0.5031, 0.0675, 0.04]
  frozen_task_target: [0.5031, -0.0925, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5030531481177555, 0.06746166958506708, 0.04]}
  frozen_targets: {'channel_exit': [0.5030531481177555, -0.09253833041493292, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de

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

## Current Skill (Q=0.327) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: approach
  anchor: object
  offset:
  - 0.0
  - 0.04
  - 0.0
- id: contact
  anchor: object
  offset:
  - 0.0
  - 0.02
  - 0.0
- id: push
  anchor: world
  offset:
  - 0.5
  - -0.08
  - 0.04
phases:
- id: align_1
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
    - 0.05
    tolerance: 0.02
    orientation:
      mode: keep_current
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: approach
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
    - 0.02
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact
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
    - 0.02
    - 0.0
    offset_along_axis:
      distance: 0.04
      axis: world_y
      mode: add_to_offset
      sign: negative
    orientation:
      mode: keep_current
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
  retries:
    max_attempts: 0
    strategy: repeat
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - -0.08
    - 0.04
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_depth:
      type: scalar
      range:
      - -0.04
      - 0.04
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
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
    tolerance: 0.05
    orientation:
      mode: none
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **align_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.05], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
  - retries: max_attempts=0, strategy=repeat
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lateral_offset_x: status=consumed; consumers=target.offset.x (replace)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0], offset_along_axis={axis=world_y, distance=0.04, mode=add_to_offset, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
  - retries: max_attempts=0, strategy=repeat
- **push_1** (`push`)
  - target: source=yaml, anchor=world, offset=[0.5, -0.08, 0.04], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset.y (add)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.05
  - orientation: mode=none
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.327
- **task_score** (E): 0.670
- **fitness_score**: 0.730  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.570

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2005 |
| approach_1 | 1.00 | 1.00 | 0.0750 |
| contact_1 | 1.00 | 1.00 | 0.0029 |
| push_1 | 1.00 | 1.00 | 0.1864 |
| backoff_1 | 1.00 | 1.00 | 0.0100 |
| lift_1 | 1.00 | 1.00 | 0.0707 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.145, 0.108) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.560 | 2.127 |
| approach_1 | approach | 1.00 / step_budget | (0.497, 0.145, 0.108)→(0.499, 0.112, 0.041) | (0.501, 0.099, 0.034)→(0.501, 0.086, 0.033) | 0.180→0.167 | 1.00 / 1.667 | 64.687 | 213.650 |
| contact_1 | contact | 1.00 / force_exceeded | (0.499, 0.112, 0.041)→(0.498, 0.110, 0.040) | (0.501, 0.086, 0.033)→(0.499, 0.084, 0.034) | 0.167→0.165 | 1.00 / 2.333 | 1342.611 | 47.091 |
| push_1 | push | 1.00 / step_budget | (0.498, 0.110, 0.040)→(0.497, -0.076, 0.036) | (0.499, 0.084, 0.034)→(0.499, -0.039, 0.028) | 0.165→0.051 | 1.00 / 2.667 | 77.040 | 145.729 |
| backoff_1 | retract | 1.00 / step_budget | (0.497, -0.076, 0.036)→(0.496, -0.066, 0.035) | (0.499, -0.039, 0.028)→(0.499, -0.036, 0.027) | 0.051→0.053 | 1.00 / 2.667 | 25.820 | 53.404 |
| lift_1 | retract | 1.00 / step_budget | (0.496, -0.066, 0.035)→(0.495, -0.060, 0.106) | (0.499, -0.036, 0.027)→(0.499, -0.035, 0.028) | 0.053→0.051 | 1.00 / 1.000 | 0.531 | 54.879 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 1.000
- phase_score: 0.666
- phase_breakdown.push_score: 0.690
- phase_breakdown.approach_score: 0.531
- phase_breakdown.contact_score: 0.730

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.800
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.362
- **K-run variance**: 0.0056
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.405


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `080f370e6b427cbdf66706e7036a0e474f3967ccfc94f129756881a980a10a27`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `1f3f20d8b9dd2cb87de5d9f0723b4addbc88cdcf096cd2177633d23c0fa32881`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61875,"average_solve_count":160.0,"average_success_count":160.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_offset_x":-0.00965,"approach_1.lateral_offset_y":0.00887,"approach_1.speed":0.09726,"backoff_1.speed":0.09918,"contact_1.contact_force_threshold":4.39201,"lift_1.retract_height":0.08988,"lift_1.speed":0.06036,"push_1.push_depth":-0.01903,"push_1.speed":0.09855},"optimized_scores":{"best_composite_score":0.36177,"best_fitness_score":0.7651,"best_task_score":0.67763},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":296.0,"contact_point_centroid":[0.50528,0.06868,0.00875],"force_p95":182.13272,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":191.34149,"mean_force":47.18619,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49586,0.09707,0.06961]},{"body_a":"attachment","body_b":"peg","contact_count":112.0,"contact_point_centroid":[0.50581,0.08173,0.05355],"force_p95":186.61254,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":190.87002,"mean_force":123.25151,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49592,0.08769,0.05285]},{"body_a":"attachment","body_b":"peg","contact_count":653.0,"contact_point_centroid":[0.50042,-0.00701,0.03786],"force_p95":114.36597,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":124.54048,"mean_force":65.54513,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49534,0.00204,0.03782]},{"body_a":"peg","body_b":"channel_base_body","contact_count":693.0,"contact_point_centroid":[0.50291,-0.02317,0.00862],"force_p95":102.70494,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":108.57365,"mean_force":53.78366,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49548,-0.00086,0.03785]},{"body_a":"peg","body_b":"channel_base_body","contact_count":55.0,"contact_point_centroid":[0.4928,-0.07249,0.00857],"force_p95":16.87829,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":88.04173,"mean_force":6.48707,"phase_index":5.0,"phase_name":"lift_1","phase_type":"retract","tcp_position_centroid":[0.49845,-0.06664,0.05384]},{"body_a":"peg","body_b":"channel_base_body","contact_count":47.0,"contact_point_centroid":[0.49298,-0.08784,0.00712],"force_p95":74.13929,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":80.98702,"mean_force":32.35677,"phase_index":4.0,"phase_name":"backoff_1","phase_type":"retract","tcp_position_centroid":[0.50004,-0.07877,0.03884]},{"body_a":"attachment","body_b":"peg","contact_count":43.0,"contact_point_centroid":[0.49536,-0.08435,0.03993],"force_p95":73.22022,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":75.74894,"mean_force":40.10608,"phase_index":4.0,"phase_name":"backoff_1","phase_type":"retract","tcp_position_centroid":[0.50004,-0.07905,0.03885]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.49532,-0.07989,0.03974],"force_p95":42.54353,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":75.4734,"mean_force":15.00259,"phase_index":5.0,"phase_name":"lift_1","phase_type":"retract","tcp_position_centroid":[0.49924,-0.06862,0.03903]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":376.0,"contact_point_centroid":[0.52539,-0.01203,0.02495],"force_p95":48.14041,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.25154,"mean_force":36.56863,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4949,0.00546,0.03773]},{"body_a":"peg","body_b":"channel_base_body","contact_count":79.0,"contact_point_centroid":[0.4937,-0.10019,0.03059],"force_p95":28.62845,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.07566,"mean_force":14.90562,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49861,-0.07452,0.03799]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.47489,-0.0656,0.02245],"force_p95":25.12809,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.02117,"mean_force":18.10108,"phase_index":4.0,"phase_name":"backoff_1","phase_type":"retract","tcp_position_centroid":[0.50001,-0.07767,0.0388]},{"body_a":"peg","body_b":"channel_base_body","contact_count":11.0,"contact_point_centroid":[0.49389,-0.10033,0.03577],"force_p95":14.72276,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.94223,"mean_force":2.85424,"phase_index":4.0,"phase_name":"backoff_1","phase_type":"retract","tcp_position_centroid":[0.50005,-0.08426,0.03893]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":41.0,"contact_point_centroid":[0.47492,-0.06566,0.02131],"force_p95":24.51669,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.09791,"mean_force":12.7687,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49814,-0.07087,0.03773]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":41.0,"contact_point_centroid":[0.47477,-0.06084,0.02529],"force_p95":16.90603,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.92103,"mean_force":6.18056,"phase_index":5.0,"phase_name":"lift_1","phase_type":"retract","tcp_position_centroid":[0.49841,-0.06678,0.04989]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":9.0,"contact_point_centroid":[0.5254,0.05246,0.05665],"force_p95":12.04976,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.12766,"mean_force":5.3855,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49855,0.08347,0.04682]},{"body_a":"peg","body_b":"channel_base_body","contact_count":24.0,"contact_point_centroid":[0.50142,0.04435,0.00958],"force_p95":0.44029,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.13941,"mean_force":0.71987,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49498,0.08027,0.04043]}],"total_contact_groups":18},"final_pose_error":0.0499,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49356,-0.06827,0.02617],"final_tcp_position":[0.49835,-0.06569,0.07845],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":191.34149,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":401.0,"n_steps_budget":1000.0,"object_pos_end":[0.50302,0.06748,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54683,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":385.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach","tcp_end":[0.49999,0.1165,0.10729],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08839,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":296.0,"n_steps_budget":600.0,"object_pos_end":[0.5045,0.05113,0.03806],"object_pos_start":[0.50302,0.06748,0.0338],"object_to_goal_dist_end":0.13123,"object_to_goal_dist_start":0.14764,"object_z_max":0.03785,"peak_contact_force":0.34103,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":417.0,"raw_peak_contact_force":191.34149,"subtask_id":"contact","tcp_end":[0.49591,0.08148,0.04178],"tcp_start":[0.49999,0.1165,0.10729],"tcp_to_object_dist_end":0.03175,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":24.0,"n_steps_budget":600.0,"object_pos_end":[0.50045,0.04613,0.04056],"object_pos_start":[0.5045,0.05113,0.03806],"object_to_goal_dist_end":0.12613,"object_to_goal_dist_start":0.13123,"object_z_max":0.04053,"peak_contact_force":8.13941,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":25.0,"raw_peak_contact_force":8.13941,"tcp_end":[0.49448,0.07883,0.03947],"tcp_start":[0.49591,0.08148,0.04178],"tcp_to_object_dist_end":0.03326,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":693.0,"n_steps_budget":1000.0,"object_pos_end":[0.49318,-0.07574,0.02399],"object_pos_start":[0.50045,0.04613,0.04056],"object_to_goal_dist_end":0.01792,"object_to_goal_dist_start":0.12613,"object_z_max":0.04065,"peak_contact_force":90.02232,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1842.0,"raw_peak_contact_force":124.54048,"tcp_end":[0.49997,-0.08418,0.03884],"tcp_start":[0.49448,0.07883,0.03947],"tcp_to_object_dist_end":0.01839,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":47.0,"n_steps_budget":600.0,"object_pos_end":[0.49299,-0.06898,0.02163],"object_pos_start":[0.49318,-0.07574,0.02399],"object_to_goal_dist_end":0.02254,"object_to_goal_dist_start":0.01792,"object_z_max":0.02411,"peak_contact_force":40.46901,"phase_name":"backoff_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":136.0,"raw_peak_contact_force":80.98702,"tcp_end":[0.49959,-0.06979,0.03828],"tcp_start":[0.49997,-0.08418,0.03884],"tcp_to_object_dist_end":0.01793,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":55.0,"n_steps_budget":930.0,"object_pos_end":[0.49356,-0.06827,0.02617],"object_pos_start":[0.49299,-0.06898,0.02163],"object_to_goal_dist_end":0.01924,"object_to_goal_dist_start":0.02254,"object_z_max":0.02726,"peak_contact_force":0.58423,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":110.0,"raw_peak_contact_force":88.04173,"tcp_end":[0.49835,-0.06569,0.07845],"tcp_start":[0.49959,-0.06979,0.03828],"tcp_to_object_dist_end":0.05256,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `625c03a21403c0f6267b643060335ee3d751a26340ace08db5429afcee4c5ccf`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.0,"average_solve_count":244.0,"average_success_count":244.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_offset_x":0.00818,"approach_1.lateral_offset_y":-0.00025,"approach_1.speed":0.01948,"backoff_1.speed":0.08318,"contact_1.contact_force_threshold":11.65774,"lift_1.retract_height":0.09497,"lift_1.speed":0.07479,"push_1.push_depth":-0.00591,"push_1.speed":0.07433},"optimized_scores":{"best_composite_score":0.39625,"best_fitness_score":0.79959,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":7,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":317.0,"contact_point_centroid":[0.52509,0.11995,0.05999],"force_p95":205.93517,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":245.15495,"mean_force":167.88628,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51364,0.12601,0.05048]},{"body_a":"peg","body_b":"channel_base_body","contact_count":629.0,"contact_point_centroid":[0.51121,0.11262,0.00869],"force_p95":164.45405,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":169.41452,"mean_force":80.13111,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51017,0.13175,0.06213]},{"body_a":"attachment","body_b":"peg","contact_count":398.0,"contact_point_centroid":[0.51832,0.11702,0.05357],"force_p95":164.91924,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":168.94525,"mean_force":125.99079,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51281,0.12615,0.05186]},{"body_a":"attachment","body_b":"peg","contact_count":506.0,"contact_point_centroid":[0.5019,-0.01366,0.04956],"force_p95":137.72396,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":140.56101,"mean_force":36.69926,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49921,-0.00271,0.03351]},{"body_a":"peg","body_b":"channel_base_body","contact_count":157.0,"contact_point_centroid":[0.50734,-0.10162,0.06014],"force_p95":128.91509,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":130.28875,"mean_force":94.09434,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49652,-0.05921,0.03405]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.50798,-0.10217,0.05987],"force_p95":73.04304,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":78.56489,"mean_force":57.77014,"phase_index":4.0,"phase_name":"backoff_1","phase_type":"retract","tcp_position_centroid":[0.49479,-0.06201,0.03261]},{"body_a":"attachment","body_b":"peg","contact_count":20.0,"contact_point_centroid":[0.50278,-0.0716,0.06122],"force_p95":68.43828,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":74.59965,"mean_force":46.44567,"phase_index":4.0,"phase_name":"backoff_1","phase_type":"retract","tcp_position_centroid":[0.49479,-0.06201,0.03261]},{"body_a":"attachment","body_b":"peg","contact_count":26.0,"contact_point_centroid":[0.50016,-0.06764,0.0549],"force_p95":56.71548,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":70.39734,"mean_force":25.64735,"phase_index":5.0,"phase_name":"lift_1","phase_type":"retract","tcp_position_centroid":[0.49278,-0.05727,0.03774]},{"body_a":"peg","body_b":"channel_base_body","contact_count":31.0,"contact_point_centroid":[0.50748,-0.101,0.06044],"force_p95":52.49108,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":54.69233,"mean_force":25.26462,"phase_index":5.0,"phase_name":"lift_1","phase_type":"retract","tcp_position_centroid":[0.49249,-0.05696,0.03762]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":138.0,"contact_point_centroid":[0.47475,0.04397,0.04031],"force_p95":38.62529,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.49381,"mean_force":9.32815,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50304,0.07122,0.03312]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":251.0,"contact_point_centroid":[0.52535,-0.06345,0.04562],"force_p95":32.71148,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.54679,"mean_force":13.70813,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49748,-0.03641,0.03376]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.52546,-0.08261,0.04675],"force_p95":27.85056,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.83645,"mean_force":7.50536,"phase_index":5.0,"phase_name":"lift_1","phase_type":"retract","tcp_position_centroid":[0.49224,-0.05584,0.0453]},{"body_a":"peg","body_b":"channel_base_body","contact_count":29.0,"contact_point_centroid":[0.50645,-0.0845,0.00967],"force_p95":11.24532,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.07612,"mean_force":3.68439,"phase_index":5.0,"phase_name":"lift_1","phase_type":"retract","tcp_position_centroid":[0.4926,-0.05552,0.05776]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":20.0,"contact_point_centroid":[0.52551,-0.08634,0.05965],"force_p95":28.06988,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.17815,"mean_force":27.28827,"phase_index":4.0,"phase_name":"backoff_1","phase_type":"retract","tcp_position_centroid":[0.49479,-0.06201,0.03261]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.52016,-0.09506,0.00976],"force_p95":18.41068,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.63059,"mean_force":9.24215,"phase_index":4.0,"phase_name":"backoff_1","phase_type":"retract","tcp_position_centroid":[0.49479,-0.06201,0.03261]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":53.0,"contact_point_centroid":[0.52514,0.10989,0.05698],"force_p95":10.17467,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.80994,"mean_force":3.9908,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51262,0.12444,0.05369]}],"total_contact_groups":23},"final_pose_error":0.04964,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50603,-0.08097,0.03405],"final_tcp_position":[0.49239,-0.05475,0.07788],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":3893.53637,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":372.0,"n_steps_budget":1000.0,"object_pos_end":[0.50375,0.11176,0.0338],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.56268,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":366.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach","tcp_end":[0.50616,0.15629,0.10861],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08709,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":644.0,"n_steps_budget":1000.0,"object_pos_end":[0.49426,0.09258,0.03384],"object_pos_start":[0.50375,0.11176,0.0338],"object_to_goal_dist_end":0.17279,"object_to_goal_dist_start":0.1919,"object_z_max":0.03672,"peak_contact_force":1.04314,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1429.0,"raw_peak_contact_force":245.15495,"subtask_id":"contact","tcp_end":[0.50986,0.12015,0.03795],"tcp_start":[0.50616,0.15629,0.10861],"tcp_to_object_dist_end":0.03194,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":26.0,"n_steps_budget":600.0,"object_pos_end":[0.4931,0.09122,0.03613],"object_pos_start":[0.49426,0.09258,0.03384],"object_to_goal_dist_end":0.1714,"object_to_goal_dist_start":0.17279,"object_z_max":0.03592,"peak_contact_force":3893.53637,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":40.0,"raw_peak_contact_force":6.97874,"tcp_end":[0.50729,0.11692,0.03552],"tcp_start":[0.50986,0.12015,0.03795],"tcp_to_object_dist_end":0.02936,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":728.0,"n_steps_budget":1000.0,"object_pos_end":[0.50685,-0.08574,0.03577],"object_pos_start":[0.4931,0.09122,0.03613],"object_to_goal_dist_end":0.00989,"object_to_goal_dist_start":0.1714,"object_z_max":0.03919,"peak_contact_force":140.56101,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1441.0,"raw_peak_contact_force":140.56101,"tcp_end":[0.49533,-0.06339,0.03315],"tcp_start":[0.50729,0.11692,0.03552],"tcp_to_object_dist_end":0.02528,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50682,-0.08493,0.0354],"object_pos_start":[0.50685,-0.08574,0.03577],"object_to_goal_dist_end":0.00959,"object_to_goal_dist_start":0.00989,"object_z_max":0.03577,"peak_contact_force":36.35858,"phase_name":"backoff_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":80.0,"raw_peak_contact_force":78.56489,"tcp_end":[0.49427,-0.0598,0.03225],"tcp_start":[0.49533,-0.06339,0.03315],"tcp_to_object_dist_end":0.02827,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":61.0,"n_steps_budget":810.0,"object_pos_end":[0.50603,-0.08097,0.03405],"object_pos_start":[0.50682,-0.08493,0.0354],"object_to_goal_dist_end":0.00853,"object_to_goal_dist_start":0.00959,"object_z_max":0.03768,"peak_contact_force":0.47539,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":123.0,"raw_peak_contact_force":70.39734,"tcp_end":[0.49239,-0.05475,0.07788],"tcp_start":[0.49427,-0.0598,0.03225],"tcp_to_object_dist_end":0.05286,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `abe38b4b57ac37a91047e57d04e408cb1fd05583a47670bcb186dc9505a3f021`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.27004,"average_solve_count":237.0,"average_success_count":237.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_offset_x":-0.00958,"approach_1.lateral_offset_y":0.00918,"approach_1.speed":0.05204,"backoff_1.speed":0.0734,"contact_1.contact_force_threshold":3.43075,"lift_1.retract_height":0.17393,"lift_1.speed":0.05117,"push_1.push_depth":-0.01373,"push_1.speed":0.06727},"optimized_scores":{"best_composite_score":0.22337,"best_fitness_score":0.6267,"best_task_score":0.33185},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":179.0,"contact_point_centroid":[0.4956,0.13,0.05088],"force_p95":187.89609,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":204.45343,"mean_force":122.62568,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48736,0.1379,0.04997]},{"body_a":"peg","body_b":"channel_base_body","contact_count":362.0,"contact_point_centroid":[0.49673,0.11939,0.00818],"force_p95":147.16949,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":184.65825,"mean_force":56.89086,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48512,0.14521,0.06752]},{"body_a":"peg","body_b":"channel_base_body","contact_count":891.0,"contact_point_centroid":[0.50586,0.0679,0.00748],"force_p95":164.58519,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":172.08682,"mean_force":83.16436,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49763,0.0385,0.04439]},{"body_a":"attachment","body_b":"peg","contact_count":560.0,"contact_point_centroid":[0.50897,0.08213,0.05036],"force_p95":163.82822,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":171.48091,"mean_force":131.41869,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49929,0.08048,0.04861]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49097,0.11936,0.0055],"force_p95":126.15613,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":126.15613,"mean_force":126.15613,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49189,0.1352,0.04435]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49904,0.12611,0.0469],"force_p95":126.06569,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":126.06569,"mean_force":126.06569,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49189,0.1352,0.04435]},{"body_a":"peg","body_b":"world","contact_count":61.0,"contact_point_centroid":[0.50174,0.1301,-0.0002],"force_p95":50.52834,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":53.19302,"mean_force":27.78872,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49055,0.13605,0.04563]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":177.0,"contact_point_centroid":[0.5251,0.08044,0.05127],"force_p95":12.91784,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.04608,"mean_force":7.48757,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50091,0.06393,0.04927]},{"body_a":"peg","body_b":"world","contact_count":12.0,"contact_point_centroid":[0.50292,0.1301,-0.00017],"force_p95":26.73302,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.92435,"mean_force":16.4508,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49224,0.13494,0.04472]},{"body_a":"peg","body_b":"channel_base_body","contact_count":150.0,"contact_point_centroid":[0.49747,0.04452,0.00809],"force_p95":0.69184,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.19914,"mean_force":0.71006,"phase_index":5.0,"phase_name":"lift_1","phase_type":"retract","tcp_position_centroid":[0.49424,-0.05884,0.09106]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":6.0,"contact_point_centroid":[0.475,0.02273,0.02425],"force_p95":5.97515,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.97554,"mean_force":3.14069,"phase_index":5.0,"phase_name":"lift_1","phase_type":"retract","tcp_position_centroid":[0.4935,-0.06232,0.05232]},{"body_a":"peg","body_b":"channel_base_body","contact_count":340.0,"contact_point_centroid":[0.49639,0.11903,0.00939],"force_p95":0.63431,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56429,"phase_index":0.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.49175,0.1803,0.19941]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.47498,0.02481,0.03074],"force_p95":1.68077,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.71126,"mean_force":1.40638,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49502,0.00839,0.03971]},{"body_a":"peg","body_b":"world","contact_count":1.0,"contact_point_centroid":[0.50281,0.13007,-0.00031],"force_p95":1.19838,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.19838,"mean_force":1.19838,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49189,0.1352,0.04435]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.49959,0.19904,0.2964]},{"body_a":"peg","body_b":"channel_base_body","contact_count":41.0,"contact_point_centroid":[0.4977,0.04391,0.00812],"force_p95":0.65733,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65873,"mean_force":0.60386,"phase_index":4.0,"phase_name":"backoff_1","phase_type":"retract","tcp_position_centroid":[0.49531,-0.07605,0.03491]}],"total_contact_groups":16},"final_pose_error":0.04926,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49808,0.04393,0.02412],"final_tcp_position":[0.4948,-0.05931,0.16027],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":204.45343,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":365.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.11913,0.03403],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19926,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.57183,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":364.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach","tcp_end":[0.48515,0.16278,0.10959],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08793,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":362.0,"n_steps_budget":990.0,"object_pos_end":[0.50298,0.11578,0.02668],"object_pos_start":[0.49602,0.11913,0.03403],"object_to_goal_dist_end":0.19625,"object_to_goal_dist_start":0.19926,"object_z_max":0.03406,"peak_contact_force":192.67652,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":602.0,"raw_peak_contact_force":204.45343,"subtask_id":"contact","tcp_end":[0.49189,0.1352,0.04435],"tcp_start":[0.48515,0.16278,0.10959],"tcp_to_object_dist_end":0.0285,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50301,0.11578,0.0267],"object_pos_start":[0.50298,0.11578,0.02668],"object_to_goal_dist_end":0.19625,"object_to_goal_dist_start":0.19625,"object_z_max":0.02668,"peak_contact_force":126.15613,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":126.15613,"tcp_end":[0.49192,0.13519,0.04435],"tcp_start":[0.49189,0.1352,0.04435],"tcp_to_object_dist_end":0.02849,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":898.0,"n_steps_budget":1000.0,"object_pos_end":[0.49819,0.04442,0.02428],"object_pos_start":[0.50301,0.11578,0.0267],"object_to_goal_dist_end":0.12543,"object_to_goal_dist_start":0.19625,"object_z_max":0.03964,"peak_contact_force":0.53683,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1642.0,"raw_peak_contact_force":172.08682,"tcp_end":[0.49586,-0.08011,0.0356],"tcp_start":[0.49192,0.13519,0.04435],"tcp_to_object_dist_end":0.12507,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":41.0,"n_steps_budget":600.0,"object_pos_end":[0.49738,0.04459,0.02418],"object_pos_start":[0.49819,0.04442,0.02428],"object_to_goal_dist_end":0.12562,"object_to_goal_dist_start":0.12543,"object_z_max":0.0243,"peak_contact_force":0.63132,"phase_name":"backoff_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":41.0,"raw_peak_contact_force":0.65873,"tcp_end":[0.49537,-0.06849,0.03473],"tcp_start":[0.49586,-0.08011,0.0356],"tcp_to_object_dist_end":0.11359,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":150.0,"n_steps_budget":1000.0,"object_pos_end":[0.49808,0.04393,0.02412],"object_pos_start":[0.49738,0.04459,0.02418],"object_to_goal_dist_end":0.12495,"object_to_goal_dist_start":0.12562,"object_z_max":0.02438,"peak_contact_force":0.53313,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":156.0,"raw_peak_contact_force":6.19914,"tcp_end":[0.4948,-0.05931,0.16027],"tcp_start":[0.49537,-0.06849,0.03473],"tcp_to_object_dist_end":0.17089,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```