## Search State

- **Seed**: 2
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.1993 | 0.22 | ❌ rejected |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 4 | 0.1123 | 0.03 | ❌ rejected |
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.1314 | 0.00 | ❌ rejected |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.2054 | 0.24 | ✅ accepted |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.4670 | 0.18 | ✅ accepted |

**Proposal policy**: task_score is 0.22 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.199) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_contact
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.05
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
    - 0.03
    - 0.08
    tolerance: 0.02
    orientation:
      mode: keep_current
  subtask_id: reach_contact
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.03
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 15.0
      default: 3.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: reach_contact
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
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.1
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
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.08], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.18, mode=add_to_offset, sign=negative}, tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.002, 0.0, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.199
- **task_score** (E): 0.220
- **fitness_score**: 0.373  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.067
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.240

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1706 |
| descend_1 | 1.00 | 1.00 | 0.0978 |
| contact_1 | 0.33 | 0.67 | 0.0400 |
| push_1 | 0.33 | 1.00 | 0.0475 |
| retract_1 | 1.00 | 1.00 | 0.0890 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.493, 0.154, 0.138) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.547 | 3.659 |
| descend_1 | descend | 1.00 / step_budget | (0.493, 0.154, 0.138)→(0.494, 0.148, 0.042) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 1.000 | 0.545 | 0.552 |
| contact_1 | contact | 0.33 / step_budget | (0.494, 0.148, 0.042)→(0.493, 0.109, 0.032) | (0.498, 0.068, 0.034)→(0.499, 0.067, 0.035) | 0.148→0.147 | 0.67 / 1.000 | 4.280 | 9.292 |
| push_1 | push | 0.33 / guard_failure | (0.492, 0.057, 0.030)→(0.490, 0.010, 0.029) | (0.499, 0.067, 0.035)→(0.502, -0.030, 0.035) | 0.147→0.053 | 1.00 / 3.333 | 25.784 | 48.901 |
| retract_1 | retract | 1.00 / step_budget | (0.490, 0.010, 0.029)→(0.487, 0.010, 0.118) | (0.502, -0.030, 0.035)→(0.502, -0.030, 0.034) | 0.053→0.053 | 1.00 / 1.000 | 0.368 | 205.584 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.856
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.357
- phase_score: 0.660
- phase_breakdown.establish_contact_score: 0.750
- phase_breakdown.complete_push_score: 0.931
- phase_breakdown.reach_pre_contact_score: 0.209

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.539
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.357
- **Median Q (composite search score)**: 0.231
- **K-run variance**: 0.0094
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.3
- **Final σ (mean)**: 0.340


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34158,"average_solve_count":202.0,"average_success_count":202.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":7.39334,"push_1.push_distance":0.16762,"push_1.push_speed":0.03084},"optimized_scores":{"best_composite_score":0.299,"best_fitness_score":0.539,"best_task_score":0.35743},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":161.0,"contact_point_centroid":[0.47498,-0.04901,0.04405],"force_p95":256.51338,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":276.42283,"mean_force":144.71839,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48678,-0.049,0.04202]},{"body_a":"channel_base_body","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54243,-0.1,0.06499],"force_p95":63.77686,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":65.61422,"mean_force":52.11962,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48711,-0.04991,0.02594]},{"body_a":"channel_base_body","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54252,-0.1,0.06499],"force_p95":34.08416,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":34.30684,"mean_force":32.08002,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4871,-0.04972,0.02592]},{"body_a":"attachment","body_b":"peg","contact_count":927.0,"contact_point_centroid":[0.49652,0.00016,0.04464],"force_p95":20.66133,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.27989,"mean_force":14.02427,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48734,0.01019,0.02622]},{"body_a":"peg","body_b":"channel_base_body","contact_count":953.0,"contact_point_centroid":[0.50962,-0.02756,0.00989],"force_p95":17.57149,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.06871,"mean_force":14.31057,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48736,0.01195,0.02624]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":524.0,"contact_point_centroid":[0.52507,-0.04405,0.06],"force_p95":12.80381,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.08813,"mean_force":11.14427,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48712,-0.01829,0.02603]},{"body_a":"peg","body_b":"link7","contact_count":883.0,"contact_point_centroid":[0.51971,-0.00825,0.06167],"force_p95":12.51309,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.91486,"mean_force":10.73208,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48726,0.00626,0.02613]},{"body_a":"attachment","body_b":"peg","contact_count":112.0,"contact_point_centroid":[0.49572,-0.05947,0.06022],"force_p95":0.66396,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.66179,"mean_force":0.49165,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48676,-0.04902,0.04275]},{"body_a":"peg","body_b":"channel_base_body","contact_count":538.0,"contact_point_centroid":[0.50647,-0.07916,0.00963],"force_p95":0.58094,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.17833,"mean_force":0.53685,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4851,-0.04927,0.07034]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52509,-0.07565,0.06],"force_p95":6.57476,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.00965,"mean_force":1.87826,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48708,-0.04993,0.02602]},{"body_a":"peg","body_b":"channel_base_body","contact_count":523.0,"contact_point_centroid":[0.49514,0.06341,0.00941],"force_p95":0.55175,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.24114,"mean_force":0.65996,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48862,0.11741,0.03412]},{"body_a":"peg","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.52026,-0.06371,0.06152],"force_p95":7.08148,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.23075,"mean_force":2.51962,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48699,-0.04995,0.02623]},{"body_a":"attachment","body_b":"peg","contact_count":19.0,"contact_point_centroid":[0.49444,0.08139,0.05128],"force_p95":6.45173,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.90821,"mean_force":3.2768,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4906,0.09336,0.03015]},{"body_a":"peg","body_b":"channel_base_body","contact_count":292.0,"contact_point_centroid":[0.49552,0.06393,0.00935],"force_p95":0.65239,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.5745,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48952,0.1736,0.21362]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49931,0.19843,0.29551]},{"body_a":"peg","body_b":"channel_base_body","contact_count":319.0,"contact_point_centroid":[0.4951,0.06394,0.0094],"force_p95":0.5501,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55295,"mean_force":0.54575,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4842,0.14665,0.08994]}],"total_contact_groups":16},"final_pose_error":0.01156,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50339,-0.07303,0.03378],"final_tcp_position":[0.48389,-0.04956,0.11483],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":276.42283,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":319.0,"n_steps_budget":1000.0,"object_pos_end":[0.4951,0.0637,0.03391],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14391,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54654,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":320.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_pre_contact","tcp_end":[0.48098,0.15033,0.13869],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13668,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":319.0,"n_steps_budget":690.0,"object_pos_end":[0.495,0.06367,0.03396],"object_pos_start":[0.4951,0.0637,0.03391],"object_to_goal_dist_end":0.14388,"object_to_goal_dist_start":0.14391,"object_z_max":0.03396,"peak_contact_force":0.54439,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":319.0,"raw_peak_contact_force":0.55295,"subtask_id":"reach_pre_contact","tcp_end":[0.48972,0.1435,0.04223],"tcp_start":[0.48098,0.15033,0.13869],"tcp_to_object_dist_end":0.08043,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":523.0,"n_steps_budget":600.0,"object_pos_end":[0.49562,0.06265,0.03491],"object_pos_start":[0.495,0.06367,0.03396],"object_to_goal_dist_end":0.1428,"object_to_goal_dist_start":0.14388,"object_z_max":0.03483,"peak_contact_force":0.02545,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":542.0,"raw_peak_contact_force":7.24114,"subtask_id":"establish_contact","tcp_end":[0.49072,0.09241,0.03004],"tcp_start":[0.48972,0.1435,0.04223],"tcp_to_object_dist_end":0.03056,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50636,-0.07353,0.03619],"object_pos_start":[0.49562,0.06265,0.03491],"object_to_goal_dist_end":0.00984,"object_to_goal_dist_start":0.1428,"object_z_max":0.03677,"peak_contact_force":34.30684,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3289.0,"raw_peak_contact_force":34.30684,"subtask_id":"complete_push","tcp_end":[0.48711,-0.04987,0.02593],"tcp_start":[0.49072,0.09241,0.03004],"tcp_to_object_dist_end":0.03218,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.50339,-0.07303,0.03378],"object_pos_start":[0.50636,-0.07353,0.03619],"object_to_goal_dist_end":0.00994,"object_to_goal_dist_start":0.00984,"object_z_max":0.03659,"peak_contact_force":0.55051,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":827.0,"raw_peak_contact_force":276.42283,"tcp_end":[0.48389,-0.04956,0.11483],"tcp_start":[0.48711,-0.04987,0.02593],"tcp_to_object_dist_end":0.08661,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68367,"average_solve_count":98.0,"average_success_count":98.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":11.24787,"push_1.push_distance":0.16033,"push_1.push_speed":0.0361},"optimized_scores":{"best_composite_score":0.06749,"best_fitness_score":0.10749,"best_task_score":0.00047},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":133.0,"contact_point_centroid":[0.47498,0.11998,0.04768],"force_p95":230.15372,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":280.29756,"mean_force":134.27346,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48343,0.12814,0.04633]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":6.0,"contact_point_centroid":[0.47497,0.11998,0.03694],"force_p95":42.22403,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":43.07643,"mean_force":36.66363,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48544,0.12553,0.0353]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.475,0.12,0.037],"force_p95":12.81574,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":12.81574,"mean_force":12.81574,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48541,0.12574,0.03537]},{"body_a":"peg","body_b":"channel_base_body","contact_count":295.0,"contact_point_centroid":[0.49454,0.05909,0.00932],"force_p95":0.63665,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.59577,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48298,0.17111,0.21292]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49864,0.1978,0.29381]},{"body_a":"peg","body_b":"channel_base_body","contact_count":124.0,"contact_point_centroid":[0.49451,0.0586,0.00939],"force_p95":0.54994,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54603,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48568,0.13214,0.03741]},{"body_a":"peg","body_b":"channel_base_body","contact_count":342.0,"contact_point_centroid":[0.49403,0.05883,0.00939],"force_p95":0.5504,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55326,"mean_force":0.54622,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47688,0.14206,0.08919]},{"body_a":"peg","body_b":"channel_base_body","contact_count":573.0,"contact_point_centroid":[0.49393,0.0589,0.0094],"force_p95":0.55029,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55169,"mean_force":0.54571,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48243,0.12607,0.07882]},{"body_a":"peg","body_b":"channel_base_body","contact_count":6.0,"contact_point_centroid":[0.5013,0.07209,0.00939],"force_p95":0.55005,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5503,"mean_force":0.54628,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48544,0.12553,0.0353]}],"total_contact_groups":9},"final_pose_error":0.01142,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49417,0.05871,0.03399],"final_tcp_position":[0.48235,0.12463,0.12426],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":280.29756,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":324.0,"n_steps_budget":1000.0,"object_pos_end":[0.49405,0.0589,0.03385],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13916,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54834,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":330.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_pre_contact","tcp_end":[0.46873,0.14593,0.13848],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13843,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":342.0,"n_steps_budget":690.0,"object_pos_end":[0.49417,0.05883,0.03388],"object_pos_start":[0.49405,0.0589,0.03385],"object_to_goal_dist_end":0.13908,"object_to_goal_dist_start":0.13916,"object_z_max":0.03388,"peak_contact_force":0.54394,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":342.0,"raw_peak_contact_force":0.55326,"subtask_id":"reach_pre_contact","tcp_end":[0.48751,0.13873,0.04138],"tcp_start":[0.46873,0.14593,0.13848],"tcp_to_object_dist_end":0.08053,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":124.0,"n_steps_budget":600.0,"object_pos_end":[0.49427,0.05899,0.03389],"object_pos_start":[0.49417,0.05883,0.03388],"object_to_goal_dist_end":0.13924,"object_to_goal_dist_start":0.13908,"object_z_max":0.0339,"peak_contact_force":12.81574,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":125.0,"raw_peak_contact_force":12.81574,"subtask_id":"establish_contact","tcp_end":[0.48542,0.12566,0.03535],"tcp_start":[0.48751,0.13873,0.04138],"tcp_to_object_dist_end":0.06727,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":6.0,"n_steps_budget":1000.0,"object_pos_end":[0.49412,0.05911,0.0339],"object_pos_start":[0.49427,0.05899,0.03389],"object_to_goal_dist_end":0.13937,"object_to_goal_dist_start":0.13924,"object_z_max":0.0339,"peak_contact_force":38.52051,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":12.0,"raw_peak_contact_force":43.07643,"subtask_id":"complete_push","tcp_end":[0.48548,0.1254,0.03522],"tcp_start":[0.48547,0.12542,0.03524],"tcp_to_object_dist_end":0.06685,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.49417,0.05871,0.03399],"object_pos_start":[0.49402,0.05907,0.0339],"object_to_goal_dist_end":0.13897,"object_to_goal_dist_start":0.13934,"object_z_max":0.03399,"peak_contact_force":0.5401,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":706.0,"raw_peak_contact_force":280.29756,"tcp_end":[0.48235,0.12463,0.12426],"tcp_start":[0.48548,0.1254,0.03522],"tcp_to_object_dist_end":0.1124,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.31731,"average_solve_count":208.0,"average_success_count":208.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":8.58096,"push_1.push_distance":0.19532,"push_1.push_speed":0.01527},"optimized_scores":{"best_composite_score":0.23139,"best_fitness_score":0.47139,"best_task_score":0.30339},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.55594,-0.1,0.065],"force_p95":66.46386,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":69.31892,"mean_force":44.65096,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49853,-0.04614,0.02547]},{"body_a":"channel_base_body","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.55566,-0.1,0.06497],"force_p95":58.78754,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":60.03308,"mean_force":48.61773,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49853,-0.04666,0.02548]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":142.0,"contact_point_centroid":[0.5347,0.02408,0.06],"force_p95":31.71845,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":34.92062,"mean_force":27.2848,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49839,0.01751,0.02542]},{"body_a":"peg","body_b":"channel_base_body","contact_count":539.0,"contact_point_centroid":[0.50618,-0.01797,0.00994],"force_p95":9.0501,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.18463,"mean_force":5.01693,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49856,0.02829,0.02563]},{"body_a":"attachment","body_b":"peg","contact_count":758.0,"contact_point_centroid":[0.5037,0.016,0.04331],"force_p95":9.05292,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.13248,"mean_force":3.39469,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4985,0.02777,0.02555]},{"body_a":"peg","body_b":"channel_base_body","contact_count":522.0,"contact_point_centroid":[0.50596,0.08027,0.00939],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.81999,"mean_force":0.66077,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50214,0.13425,0.03449]},{"body_a":"attachment","body_b":"peg","contact_count":15.0,"contact_point_centroid":[0.50523,0.09814,0.04727],"force_p95":6.82217,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.41257,"mean_force":4.18832,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50198,0.11012,0.02982]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":505.0,"contact_point_centroid":[0.52505,-0.00172,0.02282],"force_p95":2.91208,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.63701,"mean_force":0.83704,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49847,0.02708,0.02552]},{"body_a":"peg","body_b":"channel_base_body","contact_count":295.0,"contact_point_centroid":[0.50547,0.08095,0.00934],"force_p95":0.58712,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.59849,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51439,0.18122,0.2128]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50087,0.19847,0.29357]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":231.0,"contact_point_centroid":[0.52502,-0.07595,0.05025],"force_p95":0.27679,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.93287,"mean_force":0.08843,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49534,-0.04637,0.06408]},{"body_a":"attachment","body_b":"peg","contact_count":20.0,"contact_point_centroid":[0.504,-0.0585,0.05893],"force_p95":1.85961,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.88493,"mean_force":0.54584,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49696,-0.04659,0.02935]},{"body_a":"peg","body_b":"channel_base_body","contact_count":570.0,"contact_point_centroid":[0.50569,-0.07686,0.00945],"force_p95":0.59295,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.77911,"mean_force":0.53343,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49522,-0.04636,0.06953]},{"body_a":"peg","body_b":"channel_base_body","contact_count":277.0,"contact_point_centroid":[0.50604,0.08084,0.00938],"force_p95":0.55008,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55023,"mean_force":0.54677,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51633,0.16238,0.09061]}],"total_contact_groups":14},"final_pose_error":0.01147,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50699,-0.07595,0.03377],"final_tcp_position":[0.49525,-0.04633,0.1145],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":69.31892,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":324.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54473,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":331.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_pre_contact","tcp_end":[0.52827,0.16509,0.13796],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13581,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":277.0,"n_steps_budget":690.0,"object_pos_end":[0.50597,0.08086,0.03378],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":0.54612,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":277.0,"raw_peak_contact_force":0.55023,"subtask_id":"reach_pre_contact","tcp_end":[0.5056,0.16034,0.04367],"tcp_start":[0.52827,0.16509,0.13796],"tcp_to_object_dist_end":0.08009,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":522.0,"n_steps_budget":600.0,"object_pos_end":[0.50572,0.07951,0.03514],"object_pos_start":[0.50597,0.08086,0.03378],"object_to_goal_dist_end":0.15968,"object_to_goal_dist_start":0.16109,"object_z_max":0.03508,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":537.0,"raw_peak_contact_force":7.81999,"subtask_id":"establish_contact","tcp_end":[0.50201,0.10945,0.02972],"tcp_start":[0.5056,0.16034,0.04367],"tcp_to_object_dist_end":0.03065,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":976.0,"n_steps_budget":1000.0,"object_pos_end":[0.50698,-0.07561,0.03565],"object_pos_start":[0.50572,0.07951,0.03514],"object_to_goal_dist_end":0.00932,"object_to_goal_dist_start":0.15968,"object_z_max":0.03589,"peak_contact_force":4.5258,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1950.0,"raw_peak_contact_force":69.31892,"subtask_id":"complete_push","tcp_end":[0.49855,-0.04661,0.02549],"tcp_start":[0.49856,-0.04654,0.0255],"tcp_to_object_dist_end":0.03186,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.50699,-0.07595,0.03377],"object_pos_start":[0.50692,-0.07588,0.03572],"object_to_goal_dist_end":0.0102,"object_to_goal_dist_start":0.00912,"object_z_max":0.03572,"peak_contact_force":0.01423,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":824.0,"raw_peak_contact_force":60.03308,"tcp_end":[0.49525,-0.04633,0.1145],"tcp_start":[0.49855,-0.04661,0.02549],"tcp_to_object_dist_end":0.08679,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```