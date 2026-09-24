## Search State

- **Seed**: 6
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.4891 | 0.74 | ✅ accepted |
| 6 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.1237 | 0.01 | ❌ rejected |
| 5 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.4079 | 0.57 | ❌ rejected |
| 4 | approach → align → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.3377 | 0.19 | ❌ rejected |
| 3 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.1649 | 0.21 | ❌ rejected |

**Proposal policy**: task_score is 0.74 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.489) — your mutation base

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

- **Composite score**: 0.489
- **task_score** (E): 0.735
- **fitness_score**: 0.779  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2005 |
| approach_1 | 1.00 | 1.00 | 0.0732 |
| contact_1 | 1.00 | 1.00 | 0.0039 |
| push_1 | 1.00 | 1.00 | 0.1944 |
| retract_1 | 1.00 | 0.67 | 0.0890 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.145, 0.108) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.560 | 2.127 |
| approach_1 | approach | 1.00 / step_budget | (0.497, 0.145, 0.108)→(0.504, 0.114, 0.042) | (0.501, 0.099, 0.034)→(0.499, 0.088, 0.034) | 0.180→0.168 | 1.00 / 2.667 | 98.664 | 210.564 |
| contact_1 | contact | 1.00 / force_exceeded | (0.504, 0.114, 0.042)→(0.502, 0.112, 0.041) | (0.499, 0.088, 0.034)→(0.499, 0.085, 0.035) | 0.168→0.165 | 1.00 / 2.333 | 51.373 | 44.220 |
| push_1 | push | 1.00 / step_budget | (0.502, 0.112, 0.041)→(0.497, -0.082, 0.035) | (0.499, 0.085, 0.035)→(0.498, -0.060, 0.035) | 0.165→0.060 | 1.00 / 2.333 | 97.989 | 159.515 |
| retract_1 | retract | 1.00 / step_budget | (0.497, -0.082, 0.035)→(0.496, -0.074, 0.124) | (0.498, -0.060, 0.035)→(0.501, -0.072, 0.033) | 0.060→0.083 | 0.67 / 0.667 | 0.572 | 88.345 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 1.000
- phase_score: 0.825
- phase_breakdown.push_score: 0.900
- phase_breakdown.approach_score: 0.591
- phase_breakdown.contact_score: 0.834

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.895
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.537
- **K-run variance**: 0.0142
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.448


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30435,"average_solve_count":207.0,"average_success_count":207.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_offset_x":0.00247,"approach_1.lateral_offset_y":0.00943,"approach_1.speed":0.04604,"contact_1.contact_force_threshold":7.25278,"push_1.push_depth":-0.01789,"push_1.speed":0.06317,"retract_1.retract_height":0.14129,"retract_1.speed":0.04838},"optimized_scores":{"best_composite_score":0.53737,"best_fitness_score":0.82737,"best_task_score":0.8512},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":17.0,"contact_point_centroid":[0.52511,0.08429,0.05999],"force_p95":256.64333,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":266.54433,"mean_force":123.37004,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51197,0.08444,0.04949]},{"body_a":"attachment","body_b":"peg","contact_count":176.0,"contact_point_centroid":[0.51408,0.07861,0.054],"force_p95":173.18711,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":180.7948,"mean_force":126.32389,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5069,0.08747,0.05253]},{"body_a":"peg","body_b":"channel_base_body","contact_count":381.0,"contact_point_centroid":[0.50846,0.06893,0.00881],"force_p95":167.55736,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":176.58955,"mean_force":58.77099,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50305,0.0958,0.06714]},{"body_a":"peg","body_b":"channel_base_body","contact_count":105.0,"contact_point_centroid":[0.49551,-0.10556,0.05617],"force_p95":148.19974,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":152.68041,"mean_force":44.24614,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49559,-0.0685,0.07004]},{"body_a":"attachment","body_b":"peg","contact_count":67.0,"contact_point_centroid":[0.4958,-0.07982,0.06049],"force_p95":149.06186,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":152.35488,"mean_force":69.2231,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49522,-0.06884,0.0576]},{"body_a":"peg","body_b":"channel_base_body","contact_count":266.0,"contact_point_centroid":[0.49704,-0.10335,0.04734],"force_p95":97.46278,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":141.58112,"mean_force":66.14563,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49864,-0.05308,0.03562]},{"body_a":"attachment","body_b":"peg","contact_count":576.0,"contact_point_centroid":[0.50044,-0.02199,0.03748],"force_p95":100.88911,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":112.43185,"mean_force":54.45076,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50012,-0.01086,0.03619]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":41.0,"contact_point_centroid":[0.47481,-0.09821,0.03848],"force_p95":72.26354,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":73.2386,"mean_force":29.44703,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49681,-0.07082,0.03404]},{"body_a":"peg","body_b":"channel_base_body","contact_count":484.0,"contact_point_centroid":[0.49999,-0.03547,0.0098],"force_p95":64.3543,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":66.13257,"mean_force":37.87915,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50065,-0.00077,0.03652]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":16.0,"contact_point_centroid":[0.47487,-0.07805,0.05088],"force_p95":19.71677,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.01251,"mean_force":5.94958,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49611,-0.07187,0.08626]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":44.0,"contact_point_centroid":[0.5251,0.06243,0.05607],"force_p95":9.06531,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.6891,"mean_force":3.7017,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.511,0.08509,0.05016]},{"body_a":"peg","body_b":"channel_base_body","contact_count":48.0,"contact_point_centroid":[0.49816,0.04085,0.00983],"force_p95":0.48782,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.25683,"mean_force":0.58185,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5056,0.07928,0.03974]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.5042,0.06472,0.03833],"force_p95":7.04243,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.04243,"mean_force":7.04243,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50414,0.07669,0.03842]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52504,-0.07654,0.04206],"force_p95":2.74748,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.74748,"mean_force":2.74748,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49518,-0.06174,0.07249]},{"body_a":"peg","body_b":"channel_base_body","contact_count":385.0,"contact_point_centroid":[0.50304,0.06739,0.00932],"force_p95":0.61054,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56899,"phase_index":0.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.49942,0.15735,0.20055]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47484,0.03986,0.05767],"force_p95":1.18753,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.21294,"mean_force":0.97362,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50794,0.08205,0.04241]}],"total_contact_groups":17},"final_pose_error":0.04935,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49763,-0.07167,0.06147],"final_tcp_position":[0.49636,-0.0686,0.12778],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":266.54433,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":401.0,"n_steps_budget":1000.0,"object_pos_end":[0.50302,0.06748,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54683,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":385.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach","tcp_end":[0.49999,0.1165,0.10729],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08839,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":381.0,"n_steps_budget":1000.0,"object_pos_end":[0.49728,0.04688,0.03892],"object_pos_start":[0.50302,0.06748,0.0338],"object_to_goal_dist_end":0.12691,"object_to_goal_dist_start":0.14764,"object_z_max":0.0387,"peak_contact_force":0.74903,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":621.0,"raw_peak_contact_force":266.54433,"subtask_id":"contact","tcp_end":[0.50767,0.08183,0.04188],"tcp_start":[0.49999,0.1165,0.10729],"tcp_to_object_dist_end":0.03659,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":48.0,"n_steps_budget":600.0,"object_pos_end":[0.5021,0.04258,0.04062],"object_pos_start":[0.49728,0.04688,0.03892],"object_to_goal_dist_end":0.1226,"object_to_goal_dist_start":0.12691,"object_z_max":0.04062,"peak_contact_force":7.25683,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":58.0,"raw_peak_contact_force":7.25683,"tcp_end":[0.50409,0.07657,0.03838],"tcp_start":[0.50767,0.08183,0.04188],"tcp_to_object_dist_end":0.03412,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":582.0,"n_steps_budget":1000.0,"object_pos_end":[0.49398,-0.10843,0.03668],"object_pos_start":[0.5021,0.04258,0.04062],"object_to_goal_dist_end":0.02925,"object_to_goal_dist_start":0.1226,"object_z_max":0.0407,"peak_contact_force":91.12074,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1367.0,"raw_peak_contact_force":141.58112,"tcp_end":[0.49741,-0.07883,0.03476],"tcp_start":[0.50409,0.07657,0.03838],"tcp_to_object_dist_end":0.02986,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":119.0,"n_steps_budget":1000.0,"object_pos_end":[0.49763,-0.07167,0.06147],"object_pos_start":[0.49398,-0.10843,0.03668],"object_to_goal_dist_end":0.02315,"object_to_goal_dist_start":0.02925,"object_z_max":0.07077,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":189.0,"raw_peak_contact_force":152.68041,"tcp_end":[0.49636,-0.0686,0.12778],"tcp_start":[0.49741,-0.07883,0.03476],"tcp_to_object_dist_end":0.06639,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.01056,"average_solve_count":284.0,"average_success_count":284.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_offset_x":0.00759,"approach_1.lateral_offset_y":0.00693,"approach_1.speed":0.02268,"contact_1.contact_force_threshold":12.65846,"push_1.push_depth":-0.01966,"push_1.speed":0.04506,"retract_1.retract_height":0.17105,"retract_1.speed":0.05918},"optimized_scores":{"best_composite_score":0.60497,"best_fitness_score":0.89497,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":5,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":474.0,"contact_point_centroid":[0.51049,0.11293,0.0088],"force_p95":153.68299,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":159.85273,"mean_force":66.8279,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5099,0.13581,0.06486]},{"body_a":"attachment","body_b":"peg","contact_count":254.0,"contact_point_centroid":[0.51893,0.11994,0.05415],"force_p95":155.65221,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":159.37174,"mean_force":124.05629,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5134,0.12954,0.05245]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":127.0,"contact_point_centroid":[0.52503,0.11997,0.06],"force_p95":96.44543,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":142.29992,"mean_force":66.98301,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51568,0.12879,0.05033]},{"body_a":"attachment","body_b":"peg","contact_count":321.0,"contact_point_centroid":[0.49949,-0.00883,0.04126],"force_p95":73.30775,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":119.44247,"mean_force":23.03606,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50121,0.00236,0.03512]},{"body_a":"peg","body_b":"channel_base_body","contact_count":112.0,"contact_point_centroid":[0.49648,-0.10627,0.03934],"force_p95":83.08648,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":118.29549,"mean_force":45.89247,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49809,-0.06496,0.0351]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":213.0,"contact_point_centroid":[0.47467,-0.00749,0.04145],"force_p95":44.37184,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.51223,"mean_force":9.52585,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50229,0.02127,0.03538]},{"body_a":"peg","body_b":"channel_base_body","contact_count":180.0,"contact_point_centroid":[0.49404,0.00227,0.00943],"force_p95":25.59055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.81916,"mean_force":4.45495,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50313,0.04304,0.03523]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":20.0,"contact_point_centroid":[0.52596,-0.11694,0.02525],"force_p95":23.16768,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.35144,"mean_force":9.07442,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49664,-0.08056,0.03704]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":106.0,"contact_point_centroid":[0.52512,0.10927,0.05651],"force_p95":9.90536,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.19698,"mean_force":3.9938,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51458,0.12851,0.05189]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":13.0,"contact_point_centroid":[0.47486,-0.11981,0.05859],"force_p95":21.04952,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.71426,"mean_force":11.70245,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49598,-0.07972,0.0397]},{"body_a":"peg","body_b":"channel_base_body","contact_count":53.0,"contact_point_centroid":[0.49989,-0.11395,0.03653],"force_p95":10.8514,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.41149,"mean_force":2.46179,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49613,-0.07706,0.04931]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.48848,0.09031,0.00971],"force_p95":8.87816,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.19431,"mean_force":6.03275,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51161,0.12549,0.04075]},{"body_a":"attachment","body_b":"peg","contact_count":13.0,"contact_point_centroid":[0.50525,0.11475,0.04078],"force_p95":5.15544,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.85239,"mean_force":1.07447,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51096,0.12496,0.04007]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52561,-0.11034,0.02479],"force_p95":7.35316,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.51112,"mean_force":4.4629,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4977,-0.07966,0.03533]},{"body_a":"peg","body_b":"world","contact_count":79.0,"contact_point_centroid":[0.50172,-0.16676,-0.00103],"force_p95":2.19072,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.99987,"mean_force":0.73579,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49663,-0.06884,0.11488]},{"body_a":"peg","body_b":"channel_base_body","contact_count":8.0,"contact_point_centroid":[0.49417,-0.11994,0.00986],"force_p95":2.22222,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.4126,"mean_force":1.13467,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49591,-0.07358,0.06172]}],"total_contact_groups":21},"final_pose_error":0.04994,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50725,-0.18341,0.01359],"final_tcp_position":[0.49701,-0.07149,0.15726],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":159.85273,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":372.0,"n_steps_budget":1000.0,"object_pos_end":[0.50375,0.11176,0.0338],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.56268,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":366.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach","tcp_end":[0.50616,0.15629,0.10861],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08709,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":474.0,"n_steps_budget":1000.0,"object_pos_end":[0.4972,0.10058,0.03703],"object_pos_start":[0.50375,0.11176,0.0338],"object_to_goal_dist_end":0.18063,"object_to_goal_dist_start":0.1919,"object_z_max":0.03689,"peak_contact_force":93.76669,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":975.0,"raw_peak_contact_force":159.85273,"subtask_id":"contact","tcp_end":[0.51166,0.12552,0.04083],"tcp_start":[0.50616,0.15629,0.10861],"tcp_to_object_dist_end":0.02908,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":24.0,"n_steps_budget":600.0,"object_pos_end":[0.495,0.09566,0.03695],"object_pos_start":[0.4972,0.10058,0.03703],"object_to_goal_dist_end":0.17576,"object_to_goal_dist_start":0.18063,"object_z_max":0.0387,"peak_contact_force":30.6529,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":24.0,"raw_peak_contact_force":9.19431,"tcp_end":[0.50923,0.12288,0.03848],"tcp_start":[0.51166,0.12552,0.04083],"tcp_to_object_dist_end":0.03075,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":562.0,"n_steps_budget":1000.0,"object_pos_end":[0.50198,-0.11092,0.04282],"object_pos_start":[0.495,0.09566,0.03695],"object_to_goal_dist_end":0.03112,"object_to_goal_dist_start":0.17576,"object_z_max":0.04394,"peak_contact_force":1.76669,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":830.0,"raw_peak_contact_force":119.44247,"tcp_end":[0.49764,-0.08055,0.03532],"tcp_start":[0.50923,0.12288,0.03848],"tcp_to_object_dist_end":0.03159,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":144.0,"n_steps_budget":1000.0,"object_pos_end":[0.50725,-0.18341,0.01359],"object_pos_start":[0.50198,-0.11092,0.04282],"object_to_goal_dist_end":0.10698,"object_to_goal_dist_start":0.03112,"object_z_max":0.04282,"peak_contact_force":1.03367,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":173.0,"raw_peak_contact_force":26.35144,"tcp_end":[0.49701,-0.07149,0.15726],"tcp_start":[0.49764,-0.08055,0.03532],"tcp_to_object_dist_end":0.18241,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.22907,"average_solve_count":227.0,"average_success_count":227.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_offset_x":-0.00772,"approach_1.lateral_offset_y":0.00944,"approach_1.speed":0.09083,"contact_1.contact_force_threshold":8.61128,"push_1.push_depth":-0.03024,"push_1.speed":0.03358,"retract_1.retract_height":0.10032,"retract_1.speed":0.05013},"optimized_scores":{"best_composite_score":0.32508,"best_fitness_score":0.61508,"best_task_score":0.35408},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":40.0,"contact_point_centroid":[0.50002,-0.10041,0.06499],"force_p95":217.21506,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":217.52198,"mean_force":192.46313,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49611,-0.08837,0.03559]},{"body_a":"attachment","body_b":"peg","contact_count":126.0,"contact_point_centroid":[0.49633,0.13112,0.05165],"force_p95":192.0505,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":205.29422,"mean_force":117.08392,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48773,0.13864,0.05102]},{"body_a":"peg","body_b":"channel_base_body","contact_count":296.0,"contact_point_centroid":[0.49682,0.11929,0.00851],"force_p95":147.19881,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":199.60104,"mean_force":47.29293,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48531,0.14652,0.07027]},{"body_a":"peg","body_b":"channel_base_body","contact_count":712.0,"contact_point_centroid":[0.50378,0.06458,0.00766],"force_p95":162.88348,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":177.6229,"mean_force":76.25764,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49759,0.02812,0.04413]},{"body_a":"attachment","body_b":"peg","contact_count":409.0,"contact_point_centroid":[0.50848,0.08396,0.05081],"force_p95":165.71984,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":177.1216,"mean_force":132.0313,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49937,0.08149,0.04907]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49894,0.1269,0.04714],"force_p95":116.2079,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":116.2079,"mean_force":116.2079,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49198,0.1361,0.04475]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.48487,0.11932,0.00562],"force_p95":113.84964,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":113.84964,"mean_force":113.84964,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49198,0.1361,0.04475]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50036,-0.10003,0.065],"force_p95":86.00308,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":86.00308,"mean_force":86.00308,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49634,-0.08752,0.03532]},{"body_a":"peg","body_b":"world","contact_count":35.0,"contact_point_centroid":[0.50035,0.13064,-0.00019],"force_p95":44.41641,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.11892,"mean_force":28.33992,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4909,0.13679,0.04604]},{"body_a":"peg","body_b":"world","contact_count":12.0,"contact_point_centroid":[0.50125,0.13053,-0.00016],"force_p95":24.33015,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.93475,"mean_force":14.60833,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49237,0.13596,0.0451]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":20.0,"contact_point_centroid":[0.47497,0.01774,0.02499],"force_p95":9.20785,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.61378,"mean_force":3.34764,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49487,-0.00578,0.03925]},{"body_a":"peg","body_b":"world","contact_count":1.0,"contact_point_centroid":[0.50115,0.13051,-0.0003],"force_p95":3.81715,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.81715,"mean_force":3.81715,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49198,0.1361,0.04475]},{"body_a":"peg","body_b":"channel_base_body","contact_count":340.0,"contact_point_centroid":[0.49639,0.11903,0.00939],"force_p95":0.63431,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56429,"phase_index":0.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.49175,0.1803,0.19941]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.49959,0.19904,0.2964]},{"body_a":"peg","body_b":"channel_base_body","contact_count":70.0,"contact_point_centroid":[0.49772,0.0384,0.00804],"force_p95":0.68343,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68343,"mean_force":0.60701,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49485,-0.08405,0.05521]}],"total_contact_groups":15},"final_pose_error":0.04963,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49803,0.03912,0.02413],"final_tcp_position":[0.49498,-0.08269,0.08627],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":217.52198,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":365.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.11913,0.03403],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19926,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.57183,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":364.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach","tcp_end":[0.48515,0.16278,0.10959],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08793,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":296.0,"n_steps_budget":600.0,"object_pos_end":[0.50135,0.1166,0.02688],"object_pos_start":[0.49602,0.11913,0.03403],"object_to_goal_dist_end":0.19704,"object_to_goal_dist_start":0.19926,"object_z_max":0.03406,"peak_contact_force":201.47736,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":457.0,"raw_peak_contact_force":205.29422,"subtask_id":"contact","tcp_end":[0.49198,0.1361,0.04475],"tcp_start":[0.48515,0.16278,0.10959],"tcp_to_object_dist_end":0.02806,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50135,0.11658,0.02689],"object_pos_start":[0.50135,0.1166,0.02688],"object_to_goal_dist_end":0.19703,"object_to_goal_dist_start":0.19704,"object_z_max":0.02688,"peak_contact_force":116.2079,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":116.2079,"tcp_end":[0.49202,0.13608,0.04474],"tcp_start":[0.49198,0.1361,0.04475],"tcp_to_object_dist_end":0.02803,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":720.0,"n_steps_budget":1000.0,"object_pos_end":[0.49759,0.03911,0.02413],"object_pos_start":[0.50135,0.11658,0.02689],"object_to_goal_dist_end":0.12019,"object_to_goal_dist_start":0.19703,"object_z_max":0.03947,"peak_contact_force":201.0787,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1193.0,"raw_peak_contact_force":217.52198,"tcp_end":[0.49634,-0.08752,0.03532],"tcp_start":[0.49202,0.13608,0.04474],"tcp_to_object_dist_end":0.12713,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":70.0,"n_steps_budget":1000.0,"object_pos_end":[0.49803,0.03912,0.02413],"object_pos_start":[0.49759,0.03911,0.02413],"object_to_goal_dist_end":0.12018,"object_to_goal_dist_start":0.12019,"object_z_max":0.02413,"peak_contact_force":0.68343,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":71.0,"raw_peak_contact_force":86.00308,"tcp_end":[0.49498,-0.08269,0.08627],"tcp_start":[0.49634,-0.08752,0.03532],"tcp_to_object_dist_end":0.13678,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```