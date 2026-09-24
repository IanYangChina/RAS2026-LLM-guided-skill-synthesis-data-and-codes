## Search State

- **Seed**: 2
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → push → retract → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 2 | 0.1408 | 0.27 | ✅ accepted |
| 13 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | -0.0552 | 0.17 | ❌ rejected |
| 12 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 2 | -0.1294 | 0.00 | ❌ rejected |
| 11 | approach → descend → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0829 | 0.00 | ❌ rejected |
| 10 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.0254 | 0.12 | ❌ rejected |

**Proposal policy**: task_score is 0.27 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
| `object` | offset from object initial position (0.48092897073994534, 0.06387929147312987, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.48092897073994534, -0.09612070852687013, 0.04) | final destination targets |
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

## Current Skill (Q=0.141) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: approach_and_descend
  anchor: object
  offset:
  - 0.0
  - 0.02
  - 0.08
  weight: 0.3
- id: complete_push
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
    offset:
    - 0.0
    - 0.02
    - 0.08
    tolerance: 0.02
    orientation:
      mode: keep_current
  subtask_id: approach_and_descend
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.02
    - -0.01
    tolerance: 0.01
    orientation:
      mode: keep_current
  subtask_id: approach_and_descend
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
      distance: 0.18
      axis: world_y
      mode: add_to_offset
      sign: negative
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.12
      - 0.2
      default: 0.18
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
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.002
    - 0.0
    - 0.0
  subtask_id: complete_push
- id: retract_back
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.1
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
- id: retract_up
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
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.02, 0.08], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.02, -0.01], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.18, mode=add_to_offset, sign=negative}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.002, 0.0, 0.0]
- **retract_back** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.1, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **retract_up** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.141
- **task_score** (E): 0.271
- **fitness_score**: 0.331  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.190

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1950 |
| descend_1 | 1.00 | 1.00 | 0.1044 |
| push_1 | 0.00 | 1.00 | 0.0459 |
| retract_back | 1.00 | 1.00 | 0.0903 |
| retract_up | 1.00 | 1.00 | 0.0891 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.492, 0.100, 0.135) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.543 | 3.659 |
| descend_1 | descend | 1.00 / step_budget | (0.492, 0.100, 0.135)→(0.496, 0.089, 0.033) | (0.498, 0.068, 0.034)→(0.498, 0.044, 0.039) | 0.148→0.124 | 1.00 / 1.000 | 0.469 | 375.200 |
| push_1 | push | 0.00 / guard_failure | (0.494, 0.002, 0.030)→(0.493, -0.044, 0.029) | (0.498, 0.044, 0.039)→(0.503, -0.075, 0.031) | 0.124→0.012 | 1.00 / 3.667 | 28.006 | 39.523 |
| retract_back | retract | 1.00 / step_budget | (0.493, -0.044, 0.029)→(0.491, 0.047, 0.026) | (0.503, -0.075, 0.031)→(0.501, -0.073, 0.027) | 0.012→0.016 | 1.00 / 1.333 | 0.935 | 65.075 |
| retract_up | retract | 1.00 / step_budget | (0.491, 0.047, 0.026)→(0.488, 0.046, 0.115) | (0.501, -0.073, 0.027)→(0.502, -0.073, 0.028) | 0.016→0.016 | 1.00 / 1.000 | 0.616 | 217.423 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.855
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.300
- phase_score: 0.425
- phase_breakdown.approach_and_descend_score: 0.174
- phase_breakdown.complete_push_score: 0.532

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.375
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.300
- **Median Q (composite search score)**: 0.119
- **K-run variance**: 0.0010
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 11.0
- **Final σ (mean)**: 0.205


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55682,"average_solve_count":176.0,"average_success_count":176.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"push_1.push_distance":0.19128,"push_1.push_speed":0.04694},"optimized_scores":{"best_composite_score":0.18488,"best_fitness_score":0.37488,"best_task_score":0.30037},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":182.0,"contact_point_centroid":[0.47497,0.03833,0.04318],"force_p95":256.99646,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":293.49186,"mean_force":157.05986,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.4868,0.03837,0.0413]},{"body_a":"peg","body_b":"channel_base_body","contact_count":388.0,"contact_point_centroid":[0.49787,0.06512,0.00909],"force_p95":170.1415,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":201.2832,"mean_force":32.56483,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48621,0.09017,0.08048]},{"body_a":"attachment","body_b":"peg","contact_count":97.0,"contact_point_centroid":[0.5013,0.08082,0.05462],"force_p95":198.5446,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":200.79406,"mean_force":128.14708,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49245,0.08778,0.05331]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":158.0,"contact_point_centroid":[0.475,0.00167,0.02721],"force_p95":37.16778,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":42.28651,"mean_force":27.71264,"phase_index":3.0,"phase_name":"retract_back","phase_type":"retract","tcp_position_centroid":[0.48685,0.00169,0.02535]},{"body_a":"peg","body_b":"channel_base_body","contact_count":990.0,"contact_point_centroid":[0.50393,-0.02782,0.0097],"force_p95":36.18816,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.0763,"mean_force":29.62969,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49113,0.00978,0.03071]},{"body_a":"attachment","body_b":"peg","contact_count":978.0,"contact_point_centroid":[0.49708,-0.00097,0.02985],"force_p95":29.42434,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.0254,"mean_force":20.33738,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49112,0.00888,0.03069]},{"body_a":"peg","body_b":"channel_base_body","contact_count":87.0,"contact_point_centroid":[0.50648,-0.10041,0.05707],"force_p95":25.58198,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.19731,"mean_force":22.21207,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49058,-0.04866,0.02994]},{"body_a":"peg","body_b":"link7","contact_count":982.0,"contact_point_centroid":[0.51096,-0.0162,0.06864],"force_p95":23.70319,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.55277,"mean_force":20.29326,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49111,0.00917,0.03069]},{"body_a":"peg","body_b":"channel_base_body","contact_count":484.0,"contact_point_centroid":[0.50626,-0.07361,0.00944],"force_p95":0.6313,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.25567,"mean_force":0.63189,"phase_index":3.0,"phase_name":"retract_back","phase_type":"retract","tcp_position_centroid":[0.48705,-0.00516,0.02563]},{"body_a":"peg","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.51773,-0.06907,0.06523],"force_p95":11.34383,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.96639,"mean_force":3.97959,"phase_index":3.0,"phase_name":"retract_back","phase_type":"retract","tcp_position_centroid":[0.48965,-0.05189,0.02894]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":403.0,"contact_point_centroid":[0.52505,-0.05088,0.01656],"force_p95":12.39624,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.7317,"mean_force":10.66713,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49103,-0.03076,0.03053]},{"body_a":"attachment","body_b":"peg","contact_count":22.0,"contact_point_centroid":[0.49753,-0.05898,0.04549],"force_p95":4.16723,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.54352,"mean_force":0.61684,"phase_index":3.0,"phase_name":"retract_back","phase_type":"retract","tcp_position_centroid":[0.48884,-0.04874,0.028]},{"body_a":"peg","body_b":"channel_base_body","contact_count":8.0,"contact_point_centroid":[0.50655,-0.1003,0.05874],"force_p95":5.30454,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.45285,"mean_force":1.57048,"phase_index":3.0,"phase_name":"retract_back","phase_type":"retract","tcp_position_centroid":[0.48971,-0.05204,0.02901]},{"body_a":"peg","body_b":"channel_base_body","contact_count":350.0,"contact_point_centroid":[0.49544,0.06389,0.00936],"force_p95":0.62673,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56973,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48929,0.1454,0.21211]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":116.0,"contact_point_centroid":[0.52504,-0.0727,0.05847],"force_p95":0.13812,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17753,"mean_force":0.04354,"phase_index":3.0,"phase_name":"retract_back","phase_type":"retract","tcp_position_centroid":[0.48697,-0.00603,0.02555]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":11.0,"contact_point_centroid":[0.47467,0.04614,0.05763],"force_p95":1.50233,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.65942,"mean_force":0.58978,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49533,0.08683,0.04215]}],"total_contact_groups":19},"final_pose_error":0.01122,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50684,-0.07287,0.03383],"final_tcp_position":[0.48363,0.039,0.1145],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":293.49186,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":377.0,"n_steps_budget":1000.0,"object_pos_end":[0.49513,0.0637,0.03392],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14391,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.5429,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":378.0,"raw_peak_contact_force":2.44546,"subtask_id":"approach_and_descend","tcp_end":[0.48054,0.0961,0.1353],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10743,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":388.0,"n_steps_budget":720.0,"object_pos_end":[0.49898,0.04924,0.03982],"object_pos_start":[0.49513,0.0637,0.03392],"object_to_goal_dist_end":0.12924,"object_to_goal_dist_start":0.14391,"object_z_max":0.03977,"peak_contact_force":0.44996,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":496.0,"raw_peak_contact_force":201.2832,"subtask_id":"approach_and_descend","tcp_end":[0.49343,0.08533,0.03352],"tcp_start":[0.48054,0.0961,0.1353],"tcp_to_object_dist_end":0.03706,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50682,-0.07791,0.038],"object_pos_start":[0.49898,0.04924,0.03982],"object_to_goal_dist_end":0.00741,"object_to_goal_dist_start":0.12924,"object_z_max":0.04074,"peak_contact_force":22.93375,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3440.0,"raw_peak_contact_force":37.0763,"subtask_id":"complete_push","tcp_end":[0.48986,-0.05213,0.02918],"tcp_start":[0.49343,0.08533,0.03352],"tcp_to_object_dist_end":0.03209,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":484.0,"n_steps_budget":630.0,"object_pos_end":[0.50682,-0.07285,0.03383],"object_pos_start":[0.50682,-0.07791,0.038],"object_to_goal_dist_end":0.01165,"object_to_goal_dist_start":0.00741,"object_z_max":0.038,"peak_contact_force":1.43917,"phase_name":"retract_back","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":798.0,"raw_peak_contact_force":42.28651,"tcp_end":[0.48685,0.03924,0.02525],"tcp_start":[0.48986,-0.05213,0.02918],"tcp_to_object_dist_end":0.11418,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.50684,-0.07287,0.03383],"object_pos_start":[0.50682,-0.07285,0.03383],"object_to_goal_dist_end":0.01165,"object_to_goal_dist_start":0.01165,"object_z_max":0.03383,"peak_contact_force":0.54159,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":887.0,"raw_peak_contact_force":293.49186,"tcp_end":[0.48363,0.039,0.1145],"tcp_start":[0.48685,0.03924,0.02525],"tcp_to_object_dist_end":0.13986,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.21801,"average_solve_count":211.0,"average_success_count":211.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"push_1.push_distance":0.16114,"push_1.push_speed":0.02661},"optimized_scores":{"best_composite_score":0.11827,"best_fitness_score":0.30827,"best_task_score":0.25804},"replay_outcomes":[{"contacts":{"omitted_contact_groups":4,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":111.0,"contact_point_centroid":[0.47499,0.08056,0.05991],"force_p95":438.39551,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":467.66615,"mean_force":372.93407,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48414,0.08311,0.05833]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":163.0,"contact_point_centroid":[0.47497,0.04703,0.04391],"force_p95":266.02343,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":303.65402,"mean_force":156.76864,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.48677,0.04706,0.04193]},{"body_a":"peg","body_b":"channel_base_body","contact_count":445.0,"contact_point_centroid":[0.49638,0.0612,0.00933],"force_p95":54.63047,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":210.49395,"mean_force":17.49208,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47841,0.08534,0.07996]},{"body_a":"attachment","body_b":"peg","contact_count":134.0,"contact_point_centroid":[0.49411,0.07644,0.05763],"force_p95":156.00118,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":210.16771,"mean_force":56.37955,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48452,0.08314,0.05813]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":415.0,"contact_point_centroid":[0.47499,0.0031,0.02892],"force_p95":78.7993,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":90.75055,"mean_force":63.70187,"phase_index":3.0,"phase_name":"retract_back","phase_type":"retract","tcp_position_centroid":[0.48681,0.00312,0.02696]},{"body_a":"peg","body_b":"channel_base_body","contact_count":26.0,"contact_point_centroid":[0.4894,-0.10034,0.03109],"force_p95":33.67158,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.49254,"mean_force":23.24509,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48684,-0.03908,0.02879]},{"body_a":"attachment","body_b":"peg","contact_count":614.0,"contact_point_centroid":[0.4901,-0.00906,0.04058],"force_p95":12.59819,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.34326,"mean_force":4.19052,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48684,0.00283,0.02891]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":419.0,"contact_point_centroid":[0.475,0.01277,0.03087],"force_p95":35.88397,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":39.75464,"mean_force":28.21572,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48684,0.01278,0.02893]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.49017,-0.05109,0.04171],"force_p95":19.75165,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.14095,"mean_force":5.34152,"phase_index":3.0,"phase_name":"retract_back","phase_type":"retract","tcp_position_centroid":[0.48683,-0.03939,0.02854]},{"body_a":"peg","body_b":"channel_base_body","contact_count":108.0,"contact_point_centroid":[0.48622,-0.10009,0.02604],"force_p95":4.69354,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.69358,"mean_force":0.87145,"phase_index":3.0,"phase_name":"retract_back","phase_type":"retract","tcp_position_centroid":[0.48682,-0.02215,0.02743]},{"body_a":"peg","body_b":"channel_base_body","contact_count":676.0,"contact_point_centroid":[0.50545,-0.03176,0.00944],"force_p95":8.47358,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.81893,"mean_force":2.33326,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48691,0.02146,0.02904]},{"body_a":"peg","body_b":"channel_base_body","contact_count":539.0,"contact_point_centroid":[0.49859,-0.07371,0.00822],"force_p95":0.80531,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.8034,"mean_force":0.68575,"phase_index":3.0,"phase_name":"retract_back","phase_type":"retract","tcp_position_centroid":[0.48682,0.00364,0.02695]},{"body_a":"peg","body_b":"channel_base_body","contact_count":544.0,"contact_point_centroid":[0.4954,-0.07348,0.00804],"force_p95":0.72554,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.46509,"mean_force":0.63254,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.48497,0.04738,0.07042]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":12.0,"contact_point_centroid":[0.525,-0.09722,0.02727],"force_p95":6.1032,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.39959,"mean_force":2.35805,"phase_index":3.0,"phase_name":"retract_back","phase_type":"retract","tcp_position_centroid":[0.48681,-0.03677,0.02812]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":5.0,"contact_point_centroid":[0.47499,-0.04988,0.02425],"force_p95":7.97994,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.09212,"mean_force":3.37076,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.48681,0.04671,0.04944]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":283.0,"contact_point_centroid":[0.52502,-0.05548,0.02779],"force_p95":6.87555,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.88771,"mean_force":4.02229,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48684,0.00125,0.02891]}],"total_contact_groups":20},"final_pose_error":0.01154,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49512,-0.07318,0.02409],"final_tcp_position":[0.48364,0.04774,0.11541],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":467.66615,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":384.0,"n_steps_budget":1000.0,"object_pos_end":[0.49418,0.05887,0.03385],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13913,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54052,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":390.0,"raw_peak_contact_force":4.20518,"subtask_id":"approach_and_descend","tcp_end":[0.46801,0.09149,0.13513],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10957,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":449.0,"n_steps_budget":750.0,"object_pos_end":[0.49567,0.03061,0.0392],"object_pos_start":[0.49418,0.05887,0.03385],"object_to_goal_dist_end":0.1107,"object_to_goal_dist_start":0.13913,"object_z_max":0.0406,"peak_contact_force":0.49672,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":693.0,"raw_peak_contact_force":467.66615,"subtask_id":"approach_and_descend","tcp_end":[0.48962,0.08022,0.03257],"tcp_start":[0.46801,0.09149,0.13513],"tcp_to_object_dist_end":0.05042,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":845.0,"n_steps_budget":1000.0,"object_pos_end":[0.50469,-0.07436,0.02852],"object_pos_start":[0.49567,0.03061,0.0392],"object_to_goal_dist_end":0.01362,"object_to_goal_dist_start":0.1107,"object_z_max":0.0392,"peak_contact_force":34.2127,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2018.0,"raw_peak_contact_force":41.49254,"subtask_id":"complete_push","tcp_end":[0.48684,-0.03996,0.02872],"tcp_start":[0.48684,-0.03996,0.02874],"tcp_to_object_dist_end":0.03876,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.49592,-0.07361,0.02413],"object_pos_start":[0.50471,-0.07441,0.0285],"object_to_goal_dist_end":0.01759,"object_to_goal_dist_start":0.01362,"object_z_max":0.0285,"peak_contact_force":0.68341,"phase_name":"retract_back","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1093.0,"raw_peak_contact_force":90.75055,"tcp_end":[0.48685,0.04806,0.02649],"tcp_start":[0.48684,-0.03996,0.02872],"tcp_to_object_dist_end":0.12203,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":544.0,"n_steps_budget":630.0,"object_pos_end":[0.49512,-0.07318,0.02409],"object_pos_start":[0.49592,-0.07361,0.02413],"object_to_goal_dist_end":0.01798,"object_to_goal_dist_start":0.01759,"object_z_max":0.02442,"peak_contact_force":0.72551,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":712.0,"raw_peak_contact_force":303.65402,"tcp_end":[0.48364,0.04774,0.11541],"tcp_start":[0.48685,0.04806,0.02649],"tcp_to_object_dist_end":0.15196,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17195,"average_solve_count":221.0,"average_success_count":221.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"push_1.push_distance":0.1508,"push_1.push_speed":0.02787},"optimized_scores":{"best_composite_score":0.11921,"best_fitness_score":0.30921,"best_task_score":0.25547},"replay_outcomes":[{"contacts":{"omitted_contact_groups":6,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.52523,0.10439,0.05997],"force_p95":454.83174,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":456.65188,"mean_force":324.20138,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51248,0.10445,0.05338]},{"body_a":"peg","body_b":"channel_base_body","contact_count":339.0,"contact_point_centroid":[0.50706,0.08017,0.00929],"force_p95":115.45723,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":125.95655,"mean_force":18.63083,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51634,0.10643,0.08133]},{"body_a":"attachment","body_b":"peg","contact_count":67.0,"contact_point_centroid":[0.51656,0.09412,0.05551],"force_p95":123.3333,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":125.45596,"mean_force":91.67274,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51188,0.10429,0.05481]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":172.0,"contact_point_centroid":[0.53539,0.02294,0.06],"force_p95":56.3394,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":62.18851,"mean_force":40.11955,"phase_index":3.0,"phase_name":"retract_back","phase_type":"retract","tcp_position_centroid":[0.49934,0.01657,0.02511]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.5355,0.05912,0.05999],"force_p95":55.09272,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":55.12382,"mean_force":54.81278,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49945,0.05273,0.02509]},{"body_a":"attachment","body_b":"peg","contact_count":608.0,"contact_point_centroid":[0.50007,0.00076,0.02922],"force_p95":29.8004,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.00018,"mean_force":3.7624,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50228,0.01248,0.02896]},{"body_a":"peg","body_b":"channel_base_body","contact_count":47.0,"contact_point_centroid":[0.5108,-0.10047,0.02719],"force_p95":39.51361,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.66615,"mean_force":30.64794,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50234,-0.03745,0.02897]},{"body_a":"peg","body_b":"channel_base_body","contact_count":87.0,"contact_point_centroid":[0.51392,-0.10014,0.02544],"force_p95":1.57812,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.08195,"mean_force":0.95093,"phase_index":3.0,"phase_name":"retract_back","phase_type":"retract","tcp_position_centroid":[0.50001,-0.01046,0.02601]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.5004,-0.04955,0.02879],"force_p95":19.34343,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.96484,"mean_force":6.34205,"phase_index":3.0,"phase_name":"retract_back","phase_type":"retract","tcp_position_centroid":[0.50214,-0.03812,0.02862]},{"body_a":"peg","body_b":"channel_base_body","contact_count":901.0,"contact_point_centroid":[0.49783,-0.01464,0.00921],"force_p95":4.1866,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.50221,"mean_force":1.25653,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50242,0.0272,0.02912]},{"body_a":"peg","body_b":"channel_base_body","contact_count":514.0,"contact_point_centroid":[0.50042,-0.07218,0.00821],"force_p95":0.78992,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.52042,"mean_force":0.70199,"phase_index":3.0,"phase_name":"retract_back","phase_type":"retract","tcp_position_centroid":[0.49952,0.00888,0.02535]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":74.0,"contact_point_centroid":[0.47499,-0.03873,0.02684],"force_p95":7.3563,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.42255,"mean_force":5.07343,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50227,0.01903,0.02895]},{"body_a":"peg","body_b":"channel_base_body","contact_count":573.0,"contact_point_centroid":[0.49926,-0.07215,0.00807],"force_p95":0.7512,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.44637,"mean_force":0.69769,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49618,0.05228,0.06891]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":9.0,"contact_point_centroid":[0.52506,-0.0503,0.02432],"force_p95":6.94963,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.19195,"mean_force":1.82458,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49616,0.05225,0.11305]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":11.0,"contact_point_centroid":[0.47499,-0.09461,0.02426],"force_p95":6.83712,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.92419,"mean_force":3.79888,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49583,0.05221,0.06592]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.52503,-0.05029,0.02447],"force_p95":6.50238,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.66444,"mean_force":2.10654,"phase_index":3.0,"phase_name":"retract_back","phase_type":"retract","tcp_position_centroid":[0.49933,0.01273,0.02512]}],"total_contact_groups":22},"final_pose_error":0.01148,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50397,-0.07265,0.02459],"final_tcp_position":[0.4962,0.05226,0.11412],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":456.65188,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":370.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54527,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":377.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach_and_descend","tcp_end":[0.52872,0.11156,0.13521],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10838,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":345.0,"n_steps_budget":720.0,"object_pos_end":[0.49851,0.05225,0.03912],"object_pos_start":[0.50598,0.0809,0.03378],"object_to_goal_dist_end":0.13226,"object_to_goal_dist_start":0.16113,"object_z_max":0.04082,"peak_contact_force":0.4607,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":445.0,"raw_peak_contact_force":456.65188,"subtask_id":"approach_and_descend","tcp_end":[0.50616,0.10229,0.03362],"tcp_start":[0.52872,0.11156,0.13521],"tcp_to_object_dist_end":0.05091,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":908.0,"n_steps_budget":1000.0,"object_pos_end":[0.4971,-0.07386,0.02769],"object_pos_start":[0.49851,0.05225,0.03912],"object_to_goal_dist_end":0.01406,"object_to_goal_dist_start":0.13226,"object_z_max":0.03912,"peak_contact_force":26.87044,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1640.0,"raw_peak_contact_force":40.00018,"subtask_id":"complete_push","tcp_end":[0.50236,-0.0386,0.0289],"tcp_start":[0.50238,-0.03861,0.02894],"tcp_to_object_dist_end":0.03567,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":514.0,"n_steps_budget":630.0,"object_pos_end":[0.50067,-0.07227,0.02413],"object_pos_start":[0.49706,-0.07389,0.02768],"object_to_goal_dist_end":0.01767,"object_to_goal_dist_start":0.01406,"object_z_max":0.02775,"peak_contact_force":0.68343,"phase_name":"retract_back","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":795.0,"raw_peak_contact_force":62.18851,"tcp_end":[0.49949,0.05259,0.02512],"tcp_start":[0.50236,-0.0386,0.0289],"tcp_to_object_dist_end":0.12487,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.50397,-0.07265,0.02459],"object_pos_start":[0.50067,-0.07227,0.02413],"object_to_goal_dist_end":0.01753,"object_to_goal_dist_start":0.01767,"object_z_max":0.02454,"peak_contact_force":0.58089,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":658.0,"raw_peak_contact_force":55.12382,"tcp_end":[0.4962,0.05226,0.11412],"tcp_start":[0.49949,0.05259,0.02512],"tcp_to_object_dist_end":0.15388,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```