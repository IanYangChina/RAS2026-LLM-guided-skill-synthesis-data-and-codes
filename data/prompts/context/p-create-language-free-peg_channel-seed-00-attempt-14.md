## Search State

- **Seed**: 0
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.7271 | 0.79 | ✅ accepted |
| 13 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.4167 | 0.51 | ❌ rejected |
| 12 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.4533 | 0.62 | ❌ rejected |
| 11 | approach → contact → push → push → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.1528 | 0.00 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.5969 | 0.75 | ❌ rejected |

**Proposal policy**: task_score is 0.79 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.795, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.727) — your mutation base

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

- **Composite score**: 0.727
- **task_score** (E): 0.795
- **fitness_score**: 0.737  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2093 |
| contact_1 | 1.00 | 1.00 | 0.0684 |
| push_1 | 1.00 | 1.00 | 0.1787 |
| retract_1 | 1.00 | 1.00 | 0.0892 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.125, 0.107) | (0.498, 0.080, 0.040)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.544 | 2.179 |
| contact_1 | contact | 1.00 / force_exceeded | (0.495, 0.125, 0.107)→(0.496, 0.108, 0.041) | (0.500, 0.080, 0.034)→(0.500, 0.078, 0.035) | 0.161→0.158 | 1.00 / 2.000 | 11.008 | 12.027 |
| push_1 | push | 1.00 / step_budget | (0.496, 0.108, 0.041)→(0.494, -0.071, 0.038) | (0.500, 0.078, 0.035)→(0.503, -0.067, 0.030) | 0.158→0.019 | 1.00 / 3.000 | 1395.918 | 109.357 |
| retract_1 | retract | 1.00 / step_budget | (0.494, -0.071, 0.038)→(0.491, -0.070, 0.127) | (0.503, -0.067, 0.030)→(0.502, -0.067, 0.027) | 0.019→0.020 | 1.00 / 1.000 | 0.594 | 149.473 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.839
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.839
- phase_score: 0.836
- phase_breakdown.insertion_goal_score: 0.827
- phase_breakdown.pre_contact_score: 0.859

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.837
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.996
- **Median Q (composite search score)**: 0.723
- **K-run variance**: 0.0065
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.720


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37255,"average_solve_count":204.0,"average_success_count":204.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.04843,"contact_1.contact_force":5.2444,"push_1.insertion_depth":0.19999,"push_1.push_speed":0.0346},"optimized_scores":{"best_composite_score":0.82749,"best_fitness_score":0.83749,"best_task_score":0.83921},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":8.0,"contact_point_centroid":[0.5028,-0.10049,0.065],"force_p95":155.29298,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":162.58234,"mean_force":117.70348,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49936,-0.08889,0.04165]},{"body_a":"attachment","body_b":"peg","contact_count":489.0,"contact_point_centroid":[0.50354,-0.02185,0.04377],"force_p95":139.66029,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":145.5569,"mean_force":62.05876,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49903,-0.01221,0.04181]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":39.0,"contact_point_centroid":[0.49945,-0.10015,0.065],"force_p95":71.08042,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":132.77324,"mean_force":40.82148,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49731,-0.08821,0.05096]},{"body_a":"peg","body_b":"channel_base_body","contact_count":149.0,"contact_point_centroid":[0.50793,-0.10136,0.02831],"force_p95":102.10919,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":104.56179,"mean_force":81.58424,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50148,-0.05178,0.04436]},{"body_a":"peg","body_b":"channel_base_body","contact_count":492.0,"contact_point_centroid":[0.50585,-0.03998,0.00926],"force_p95":80.52445,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":84.17668,"mean_force":41.23016,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49932,-0.01885,0.04211]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":478.0,"contact_point_centroid":[0.5254,-0.03093,0.03241],"force_p95":38.824,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.409,"mean_force":17.67185,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49886,-0.00683,0.04165]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":29.0,"contact_point_centroid":[0.47473,-0.09729,0.02458],"force_p95":17.11738,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.63272,"mean_force":7.41672,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49949,-0.08544,0.04184]},{"body_a":"attachment","body_b":"peg","contact_count":13.0,"contact_point_centroid":[0.49547,-0.08835,0.04315],"force_p95":15.24637,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.64603,"mean_force":5.1501,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49911,-0.08876,0.04221]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":21.0,"contact_point_centroid":[0.47491,-0.0713,0.02584],"force_p95":14.67896,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.60426,"mean_force":5.0441,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49879,-0.08834,0.04272]},{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.50197,-0.07252,0.00817],"force_p95":0.76137,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.27692,"mean_force":0.87797,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49636,-0.08845,0.08541]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":18.0,"contact_point_centroid":[0.52505,-0.08448,0.0245],"force_p95":9.64371,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.7527,"mean_force":4.41978,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49618,-0.08871,0.10232]},{"body_a":"peg","body_b":"channel_base_body","contact_count":273.0,"contact_point_centroid":[0.50387,0.06086,0.00938],"force_p95":0.55048,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.04507,"mean_force":0.60471,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50281,0.09878,0.06949]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50293,0.07921,0.05568],"force_p95":8.81056,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.8312,"mean_force":8.62483,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50085,0.09126,0.04554]},{"body_a":"peg","body_b":"channel_base_body","contact_count":680.0,"contact_point_centroid":[0.50362,0.06158,0.00935],"force_p95":0.58245,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55851,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50275,0.15182,0.19361]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49978,0.19902,0.29839]}],"total_contact_groups":15},"final_pose_error":0.01147,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50642,-0.07269,0.02414],"final_tcp_position":[0.49647,-0.08878,0.13061],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":162.58234,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":703.0,"n_steps_budget":1000.0,"object_pos_end":[0.50376,0.0616,0.03378],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14179,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.54769,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":699.0,"raw_peak_contact_force":2.17216,"subtask_id":"pre_contact","tcp_end":[0.507,0.10664,0.09595],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07684,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":273.0,"n_steps_budget":600.0,"object_pos_end":[0.50378,0.06118,0.03446],"object_pos_start":[0.50376,0.0616,0.03378],"object_to_goal_dist_end":0.14134,"object_to_goal_dist_start":0.14179,"object_z_max":0.03441,"peak_contact_force":9.04507,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":275.0,"raw_peak_contact_force":9.04507,"tcp_end":[0.50078,0.09088,0.04433],"tcp_start":[0.507,0.10664,0.09595],"tcp_to_object_dist_end":0.03143,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":613.0,"n_steps_budget":1000.0,"object_pos_end":[0.49305,-0.07283,0.02575],"object_pos_start":[0.50378,0.06118,0.03446],"object_to_goal_dist_end":0.0174,"object_to_goal_dist_start":0.14134,"object_z_max":0.0401,"peak_contact_force":162.58234,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1645.0,"raw_peak_contact_force":162.58234,"subtask_id":"insertion_goal","tcp_end":[0.49944,-0.08936,0.04168],"tcp_start":[0.50078,0.09088,0.04433],"tcp_to_object_dist_end":0.02383,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.50642,-0.07269,0.02414],"object_pos_start":[0.49305,-0.07283,0.02575],"object_to_goal_dist_end":0.0186,"object_to_goal_dist_start":0.0174,"object_z_max":0.02588,"peak_contact_force":0.66715,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":634.0,"raw_peak_contact_force":132.77324,"tcp_end":[0.49647,-0.08878,0.13061],"tcp_start":[0.49944,-0.08936,0.04168],"tcp_to_object_dist_end":0.10814,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34466,"average_solve_count":206.0,"average_success_count":206.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.04694,"contact_1.contact_force":8.89125,"push_1.insertion_depth":0.19826,"push_1.push_speed":0.01099},"optimized_scores":{"best_composite_score":0.72308,"best_fitness_score":0.73308,"best_task_score":0.9959},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":299.0,"contact_point_centroid":[0.49945,0.02836,0.04192],"force_p95":30.0604,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.00297,"mean_force":6.95201,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49322,0.03905,0.03409]},{"body_a":"peg","body_b":"channel_base_body","contact_count":215.0,"contact_point_centroid":[0.50575,0.02757,0.00971],"force_p95":23.53799,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.32113,"mean_force":7.26597,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49331,0.06916,0.03413]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":330.0,"contact_point_centroid":[0.52529,0.02638,0.03235],"force_p95":18.7745,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.46155,"mean_force":3.6778,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49313,0.05303,0.03393]},{"body_a":"peg","body_b":"channel_base_body","contact_count":317.0,"contact_point_centroid":[0.50116,0.11221,0.00949],"force_p95":4.18604,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.0769,"mean_force":0.83528,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4959,0.15013,0.06656]},{"body_a":"attachment","body_b":"peg","contact_count":27.0,"contact_point_centroid":[0.49892,0.13219,0.05104],"force_p95":7.50753,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.81578,"mean_force":3.82728,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4964,0.1441,0.04401]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52513,-0.06333,0.04677],"force_p95":6.47403,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.54578,"mean_force":2.70349,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49156,-0.03691,0.0389]},{"body_a":"attachment","body_b":"peg","contact_count":13.0,"contact_point_centroid":[0.49933,-0.04765,0.0553],"force_p95":5.36301,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.40728,"mean_force":3.27926,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49145,-0.03692,0.03894]},{"body_a":"peg","body_b":"channel_base_body","contact_count":614.0,"contact_point_centroid":[0.50085,0.11602,0.00938],"force_p95":0.62539,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55646,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49801,0.17835,0.19536]},{"body_a":"peg","body_b":"channel_base_body","contact_count":538.0,"contact_point_centroid":[0.50607,-0.06518,0.00942],"force_p95":0.64352,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.69334,"mean_force":0.56314,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49027,-0.03638,0.07867]}],"total_contact_groups":9},"final_pose_error":0.01117,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50603,-0.06474,0.03382],"final_tcp_position":[0.49037,-0.0363,0.12339],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":3917.82101,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":630.0,"n_steps_budget":1000.0,"object_pos_end":[0.50092,0.11599,0.03386],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19609,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.54297,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":614.0,"raw_peak_contact_force":1.92055,"subtask_id":"pre_contact","tcp_end":[0.49766,0.15793,0.09613],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07515,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":322.0,"n_steps_budget":600.0,"object_pos_end":[0.50098,0.11289,0.03519],"object_pos_start":[0.50092,0.11599,0.03386],"object_to_goal_dist_end":0.19295,"object_to_goal_dist_start":0.19609,"object_z_max":0.03552,"peak_contact_force":10.78843,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":344.0,"raw_peak_contact_force":8.0769,"tcp_end":[0.49668,0.14264,0.03846],"tcp_start":[0.49766,0.15793,0.09613],"tcp_to_object_dist_end":0.03024,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":481.0,"n_steps_budget":1000.0,"object_pos_end":[0.50689,-0.06353,0.03661],"object_pos_start":[0.50098,0.11289,0.03519],"object_to_goal_dist_end":0.01817,"object_to_goal_dist_start":0.19295,"object_z_max":0.03818,"peak_contact_force":3917.82101,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":844.0,"raw_peak_contact_force":41.00297,"subtask_id":"insertion_goal","tcp_end":[0.49333,-0.03661,0.03415],"tcp_start":[0.49668,0.14264,0.03846],"tcp_to_object_dist_end":0.03024,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":545.0,"n_steps_budget":630.0,"object_pos_end":[0.50603,-0.06474,0.03382],"object_pos_start":[0.50689,-0.06353,0.03661],"object_to_goal_dist_end":0.01753,"object_to_goal_dist_start":0.01817,"object_z_max":0.0367,"peak_contact_force":0.54808,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":570.0,"raw_peak_contact_force":6.54578,"tcp_end":[0.49037,-0.0363,0.12339],"tcp_start":[0.49333,-0.03661,0.03415],"tcp_to_object_dist_end":0.09527,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45977,"average_solve_count":174.0,"average_success_count":174.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08076,"contact_1.contact_force":9.24298,"push_1.insertion_depth":0.19615,"push_1.push_speed":0.04412},"optimized_scores":{"best_composite_score":0.63064,"best_fitness_score":0.64064,"best_task_score":0.54916},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":87.0,"contact_point_centroid":[0.47498,-0.08529,0.05037],"force_p95":246.14393,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":309.09958,"mean_force":130.09202,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48683,-0.08528,0.04858]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":206.0,"contact_point_centroid":[0.47499,0.00671,0.03884],"force_p95":110.58564,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":124.48455,"mean_force":76.08152,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48685,0.00671,0.03707]},{"body_a":"attachment","body_b":"peg","contact_count":528.0,"contact_point_centroid":[0.497,-0.01446,0.03854],"force_p95":108.46883,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":113.4742,"mean_force":65.35337,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48701,-0.01096,0.03717]},{"body_a":"peg","body_b":"channel_base_body","contact_count":577.0,"contact_point_centroid":[0.5077,-0.02036,0.00857],"force_p95":106.21171,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":112.34417,"mean_force":43.37479,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48703,-0.00443,0.03712]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":510.0,"contact_point_centroid":[0.52593,-0.02859,0.02687],"force_p95":95.34444,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":100.01527,"mean_force":49.88355,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48699,-0.01589,0.0372]},{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.49709,-0.06453,0.0083],"force_p95":17.66534,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":93.6665,"mean_force":2.5571,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48553,-0.08526,0.0823]},{"body_a":"attachment","body_b":"peg","contact_count":49.0,"contact_point_centroid":[0.49819,-0.08561,0.04062],"force_p95":54.82217,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":85.08587,"mean_force":27.74473,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.487,-0.08613,0.04154]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":64.0,"contact_point_centroid":[0.52548,-0.08237,0.02685],"force_p95":45.59571,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.58773,"mean_force":22.56842,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48696,-0.08594,0.04271]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":8.0,"contact_point_centroid":[0.47492,0.06023,0.04669],"force_p95":21.6023,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.11751,"mean_force":9.19141,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48781,0.09037,0.03774]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47498,0.0945,0.05993],"force_p95":18.95935,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":18.95935,"mean_force":18.95935,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48683,0.09448,0.05819]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":29.0,"contact_point_centroid":[0.47494,-0.05982,0.02456],"force_p95":9.72219,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.04339,"mean_force":3.99375,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48495,-0.08526,0.08704]},{"body_a":"peg","body_b":"channel_base_body","contact_count":521.0,"contact_point_centroid":[0.49567,0.06191,0.00943],"force_p95":0.58615,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.68156,"mean_force":0.64873,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48312,0.09997,0.08318]},{"body_a":"attachment","body_b":"peg","contact_count":31.0,"contact_point_centroid":[0.4918,0.08006,0.05167],"force_p95":7.13015,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.4097,"mean_force":2.05509,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48876,0.09177,0.04597]},{"body_a":"peg","body_b":"channel_base_body","contact_count":573.0,"contact_point_centroid":[0.49532,0.06382,0.00937],"force_p95":0.57978,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56038,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48854,0.15323,0.20989]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49931,0.19837,0.29708]}],"total_contact_groups":15},"final_pose_error":0.01124,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49326,-0.06291,0.02419],"final_tcp_position":[0.48512,-0.08537,0.12742],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":309.09958,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":600.0,"n_steps_budget":1000.0,"object_pos_end":[0.49526,0.06374,0.03395],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14394,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54171,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":601.0,"raw_peak_contact_force":2.44546,"subtask_id":"pre_contact","tcp_end":[0.47927,0.10982,0.12863],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10651,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":529.0,"n_steps_budget":630.0,"object_pos_end":[0.49382,0.06096,0.03538],"object_pos_start":[0.49526,0.06374,0.03395],"object_to_goal_dist_end":0.14117,"object_to_goal_dist_start":0.14394,"object_z_max":0.03605,"peak_contact_force":13.18967,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":553.0,"raw_peak_contact_force":18.95935,"tcp_end":[0.48972,0.09053,0.04018],"tcp_start":[0.47927,0.10982,0.12863],"tcp_to_object_dist_end":0.03024,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":631.0,"n_steps_budget":1000.0,"object_pos_end":[0.50842,-0.06472,0.02761],"object_pos_start":[0.49382,0.06096,0.03538],"object_to_goal_dist_end":0.0214,"object_to_goal_dist_start":0.14117,"object_z_max":0.04026,"peak_contact_force":107.3493,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1829.0,"raw_peak_contact_force":124.48455,"subtask_id":"insertion_goal","tcp_end":[0.48804,-0.08596,0.03825],"tcp_start":[0.48972,0.09053,0.04018],"tcp_to_object_dist_end":0.0313,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.49326,-0.06291,0.02419],"object_pos_start":[0.50842,-0.06472,0.02761],"object_to_goal_dist_end":0.02423,"object_to_goal_dist_start":0.0214,"object_z_max":0.02791,"peak_contact_force":0.56717,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":772.0,"raw_peak_contact_force":309.09958,"tcp_end":[0.48512,-0.08537,0.12742],"tcp_start":[0.48804,-0.08596,0.03825],"tcp_to_object_dist_end":0.10595,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```