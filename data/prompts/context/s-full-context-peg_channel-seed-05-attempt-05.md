## Search State

- **Seed**: 5
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 8 | -0.1804 | 0.19 | ✅ accepted |
| 4 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1141 | 0.14 | ✅ accepted |
| 3 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 2 | -0.0183 | 0.00 | ❌ rejected |
| 2 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | -0.2993 | 0.00 | ✅ accepted |
| 1 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 3 | -0.0544 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.19 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`
- Frozen object start: [0.5244002338996304, 0.1046352631789195, 0.04]
- Frozen task target: [0.5244002338996304, -0.05536473682108051, 0.04]
- Goal object position: (0.5244002338996304, -0.05536473682108051, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5244002338996304, 0.1046352631789195, 0.04)
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
  frozen_object_start: [0.5244, 0.1046, 0.04]
  frozen_task_target: [0.5244, -0.0554, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5244002338996304, 0.1046352631789195, 0.04]}
  frozen_targets: {'channel_exit': [0.5244002338996304, -0.05536473682108051, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e

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
| `object` | offset from object initial position (0.5244002338996304, 0.1046352631789195, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5244002338996304, -0.05536473682108051, 0.04) | final destination targets |
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

## Current Skill (Q=-0.180) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_approach
  anchor: object
  offset:
  - 0.0
  - 0.015
  - -0.01
  weight: 0.3
- id: push_to_goal
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_behind
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
    - 0.015
    - -0.01
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tol:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
  subtask_id: reach_approach
- id: push_channel
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.15
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_duration:
      type: scalar
      range:
      - 5.0
      - 15.0
      default: 10.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_retry_offset_y:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: retry.offset.y
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.02
    - 0.0
  subtask_id: push_to_goal
- id: retract_away
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - 0.2
    - 0.3
    tolerance: 0.05
    orientation:
      mode: none
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
    retract_tol:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.015, -0.01], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tol: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.005, 0.0]
- **push_channel** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.2, mode=replace_offset_projection, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_duration: status=consumed; consumers=duration.max_time (replace)
    - push_retry_offset_y: status=consumed; consumers=retry.offset.y (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.02, 0.0]
- **retract_away** (`retract`)
  - target: source=yaml, anchor=world, offset=[0.5, 0.2, 0.3], tolerance=0.05
  - orientation: mode=none
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)
    - retract_tol: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: -0.180
- **task_score** (E): 0.186
- **fitness_score**: 0.250  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.2589 |
| push_channel | 1.00 | 1.00 | 0.0237 |
| retract_away | 1.00 | 1.00 | 0.2186 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.509, 0.119, 0.055) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 2.000 | 327.925 | 397.668 |
| push_channel | push | 1.00 / time_limit | (0.509, 0.119, 0.055)→(0.514, 0.098, 0.053) | (0.504, 0.095, 0.034)→(0.505, 0.063, 0.032) | 0.175→0.144 | 1.00 / 3.000 | 328.190 | 513.724 |
| retract_away | retract | 1.00 / step_budget | (0.514, 0.098, 0.053)→(0.503, 0.183, 0.254) | (0.505, 0.063, 0.032)→(0.504, 0.064, 0.031) | 0.144→0.144 | 1.00 / 1.000 | 0.578 | 426.345 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.489
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.489
- phase_score: 0.454
- phase_breakdown.push_to_goal_score: 0.401
- phase_breakdown.reach_approach_score: 0.575

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.468
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.489
- **Median Q (composite search score)**: -0.284
- **K-run variance**: 0.0238
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.354


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `9b36d26f861d7a613dfb3d8c86d70470e42095a430c2befa4bd6e530468a8a7e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `2af86d8f59685db6584febc0596b9044223ae39cea3120c112c665a54a1c4732`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.77174,"average_solve_count":92.0,"average_success_count":92.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.19509,"approach_behind.approach_tol":0.02666,"push_channel.push_distance":0.29082,"push_channel.push_duration":14.92302,"push_channel.push_retry_offset_y":0.00635,"push_channel.push_speed":0.14666,"retract_away.retract_speed":0.21261,"retract_away.retract_tol":0.08879},"optimized_scores":{"best_composite_score":-0.29546,"best_fitness_score":0.13454,"best_task_score":0.02076},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":899.0,"contact_point_centroid":[0.52502,0.1199,0.04754],"force_p95":212.26762,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":500.0951,"mean_force":186.87025,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5173,0.11807,0.0555]},{"body_a":"world","body_b":"link7","contact_count":150.0,"contact_point_centroid":[0.51321,0.1823,-6e-05],"force_p95":213.66368,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":427.93937,"mean_force":141.10832,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51888,0.12244,0.05514]},{"body_a":"world","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.52174,0.1886,-0.00092],"force_p95":366.9031,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":367.52175,"mean_force":334.84608,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.51956,0.12702,0.05295]},{"body_a":"world","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.49697,0.17527,-5e-05],"force_p95":256.13021,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":266.80831,"mean_force":160.02735,"phase_index":2.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.51864,0.11729,0.05437]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52503,0.11994,0.04471],"force_p95":159.36524,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":169.51083,"mean_force":100.12724,"phase_index":2.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.51864,0.11727,0.05449]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50388,0.08537,0.00992],"force_p95":1.56453,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.50552,"mean_force":1.04004,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51751,0.11882,0.0555]},{"body_a":"attachment","body_b":"peg","contact_count":895.0,"contact_point_centroid":[0.50643,0.11574,0.05137],"force_p95":1.36251,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.48567,"mean_force":0.72463,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5173,0.11809,0.0555]},{"body_a":"peg","body_b":"channel_base_body","contact_count":449.0,"contact_point_centroid":[0.50549,0.10461,0.00937],"force_p95":0.57911,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57152,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50441,0.1667,0.15846]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50392,0.21857,0.28968]},{"body_a":"peg","body_b":"channel_base_body","contact_count":218.0,"contact_point_centroid":[0.5054,0.09786,0.00949],"force_p95":0.7174,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.87311,"mean_force":0.54307,"phase_index":2.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.5107,0.15043,0.14955]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50778,0.11266,0.05233],"force_p95":0.49259,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.50888,"mean_force":0.35158,"phase_index":2.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.51865,0.11727,0.05442]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.52504,0.10112,0.05997],"force_p95":0.14142,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1637,"mean_force":0.03297,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51957,0.11974,0.05522]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52507,0.09997,0.05918],"force_p95":0.15168,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16036,"mean_force":0.09143,"phase_index":2.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.51476,0.12715,0.08308]}],"total_contact_groups":13},"final_pose_error":0.04928,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50558,0.09801,0.03398],"final_tcp_position":[0.50373,0.18627,0.25282],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":500.0951,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":476.0,"n_steps_budget":930.0,"object_pos_end":[0.50589,0.10472,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18492,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":322.70277,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":505.0,"raw_peak_contact_force":367.52175,"subtask_id":"reach_approach","tcp_end":[0.51955,0.12785,0.05445],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.03386,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50547,0.0961,0.03635],"object_pos_start":[0.50589,0.10472,0.03384],"object_to_goal_dist_end":0.17622,"object_to_goal_dist_start":0.18492,"object_z_max":0.03668,"peak_contact_force":192.87582,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2952.0,"raw_peak_contact_force":500.0951,"subtask_id":"push_to_goal","tcp_end":[0.51862,0.11733,0.05432],"tcp_start":[0.51955,0.12785,0.05445],"tcp_to_object_dist_end":0.03077,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":218.0,"n_steps_budget":780.0,"object_pos_end":[0.50558,0.09801,0.03398],"object_pos_start":[0.50547,0.0961,0.03635],"object_to_goal_dist_end":0.1782,"object_to_goal_dist_start":0.17622,"object_z_max":0.03638,"peak_contact_force":0.54359,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":233.0,"raw_peak_contact_force":266.80831,"tcp_end":[0.50373,0.18627,0.25282],"tcp_start":[0.51862,0.11733,0.05432],"tcp_to_object_dist_end":0.23597,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `314cefd2153cfe84bc0d0d2dfbeb7f4daf8feaf5f2c7ce7d396802b52a157f39`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.32479,"average_solve_count":117.0,"average_success_count":117.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.15129,"approach_behind.approach_tol":0.03042,"push_channel.push_distance":0.19668,"push_channel.push_duration":9.07365,"push_channel.push_retry_offset_y":0.02098,"push_channel.push_speed":0.12531,"retract_away.retract_speed":0.12636,"retract_away.retract_tol":0.04487},"optimized_scores":{"best_composite_score":-0.28351,"best_fitness_score":0.14649,"best_task_score":0.04934},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":28.0,"contact_point_centroid":[0.50266,0.15487,-0.00091],"force_p95":406.24751,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":411.27208,"mean_force":366.56044,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50046,0.09338,0.05306]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":808.0,"contact_point_centroid":[0.46919,0.11988,0.0572],"force_p95":235.48943,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":386.41583,"mean_force":223.34105,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50543,0.08597,0.05295]},{"body_a":"world","body_b":"link7","contact_count":141.0,"contact_point_centroid":[0.50338,0.15096,-7e-05],"force_p95":145.53987,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":254.87024,"mean_force":112.99173,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50104,0.09006,0.0554]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.46652,0.11991,0.05245],"force_p95":126.82837,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":129.16703,"mean_force":77.96312,"phase_index":2.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.50914,0.09267,0.0526]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.50273,0.08514,0.04338],"force_p95":20.13773,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.80818,"mean_force":7.31539,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50112,0.08532,0.05525]},{"body_a":"peg","body_b":"channel_base_body","contact_count":950.0,"contact_point_centroid":[0.50246,0.06042,0.00945],"force_p95":0.55823,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.53153,"mean_force":0.58935,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50478,0.08669,0.05332]},{"body_a":"peg","body_b":"channel_base_body","contact_count":512.0,"contact_point_centroid":[0.50301,0.06742,0.00934],"force_p95":0.55752,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56344,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49517,0.15123,0.16379]},{"body_a":"peg","body_b":"channel_base_body","contact_count":240.0,"contact_point_centroid":[0.50254,0.05954,0.00941],"force_p95":0.55192,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55749,"mean_force":0.5453,"phase_index":2.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.50492,0.13589,0.149]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":13.0,"contact_point_centroid":[0.525,0.11994,0.03595],"force_p95":0.0,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50128,0.07978,0.05512]}],"total_contact_groups":9},"final_pose_error":0.04959,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50257,0.05957,0.03396],"final_tcp_position":[0.50183,0.18232,0.2537],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":411.27208,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":528.0,"n_steps_budget":1000.0,"object_pos_end":[0.50304,0.0675,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":353.99542,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":540.0,"raw_peak_contact_force":411.27208,"subtask_id":"reach_approach","tcp_end":[0.5005,0.09419,0.05489],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.03411,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":961.0,"n_steps_budget":990.0,"object_pos_end":[0.50244,0.05937,0.03409],"object_pos_start":[0.50304,0.0675,0.0338],"object_to_goal_dist_end":0.13951,"object_to_goal_dist_start":0.14766,"object_z_max":0.03593,"peak_contact_force":206.99147,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1918.0,"raw_peak_contact_force":386.41583,"subtask_id":"push_to_goal","tcp_end":[0.50921,0.09263,0.05262],"tcp_start":[0.5005,0.09419,0.05489],"tcp_to_object_dist_end":0.03868,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":240.0,"n_steps_budget":1000.0,"object_pos_end":[0.50257,0.05957,0.03396],"object_pos_start":[0.50244,0.05937,0.03409],"object_to_goal_dist_end":0.13972,"object_to_goal_dist_start":0.13951,"object_z_max":0.03409,"peak_contact_force":0.54685,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":244.0,"raw_peak_contact_force":129.16703,"tcp_end":[0.50183,0.18232,0.2537],"tcp_start":[0.50921,0.09263,0.05262],"tcp_to_object_dist_end":0.2517,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7acce370299b32aeef0e4239da3e97eae076cb9602edead185a6cf774ee0bc4e`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.19048,"average_solve_count":147.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.07025,"approach_behind.approach_tol":0.01933,"push_channel.push_distance":0.2208,"push_channel.push_duration":13.31892,"push_channel.push_retry_offset_y":0.02695,"push_channel.push_speed":0.08811,"retract_away.retract_speed":0.19089,"retract_away.retract_tol":0.05264},"optimized_scores":{"best_composite_score":0.03763,"best_fitness_score":0.46763,"best_task_score":0.4887},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.47496,0.11992,0.05366],"force_p95":875.28361,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":883.05894,"mean_force":492.68931,"phase_index":2.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.51325,0.08428,0.05205]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":500.0,"contact_point_centroid":[0.47496,0.11993,0.05393],"force_p95":317.85422,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":654.66121,"mean_force":233.08383,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51001,0.08179,0.05382]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.52507,0.0862,0.05214],"force_p95":538.75795,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":544.23995,"mean_force":294.88702,"phase_index":2.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.51329,0.08426,0.05204]},{"body_a":"world","body_b":"link7","contact_count":35.0,"contact_point_centroid":[0.50862,0.19468,-0.00073],"force_p95":386.98026,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":414.20901,"mean_force":322.05148,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50619,0.13361,0.05387]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":28.0,"contact_point_centroid":[0.52507,0.08594,0.05218],"force_p95":391.0334,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":407.51142,"mean_force":236.79815,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51329,0.08402,0.05208]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":77.0,"contact_point_centroid":[0.52501,0.11981,0.03123],"force_p95":342.7086,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":386.84301,"mean_force":141.6657,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50619,0.08007,0.05606]},{"body_a":"world","body_b":"link7","contact_count":353.0,"contact_point_centroid":[0.50837,0.17265,-3e-05],"force_p95":121.21364,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":349.85714,"mean_force":109.0091,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50573,0.11241,0.05619]},{"body_a":"peg","body_b":"channel_base_body","contact_count":988.0,"contact_point_centroid":[0.50571,0.06521,0.00941],"force_p95":27.27985,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.1012,"mean_force":4.76855,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50788,0.09496,0.055]},{"body_a":"attachment","body_b":"peg","contact_count":463.0,"contact_point_centroid":[0.50566,0.09743,0.04417],"force_p95":34.99858,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.08187,"mean_force":9.10709,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50593,0.09768,0.05607]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":69.0,"contact_point_centroid":[0.52503,0.04329,0.05793],"force_p95":1.04452,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.70669,"mean_force":0.73305,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50723,0.08042,0.05535]},{"body_a":"peg","body_b":"channel_base_body","contact_count":550.0,"contact_point_centroid":[0.5035,0.11168,0.00937],"force_p95":0.61124,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55839,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49853,0.17107,0.16714]},{"body_a":"peg","body_b":"channel_base_body","contact_count":239.0,"contact_point_centroid":[0.50521,0.0337,0.00807],"force_p95":0.64362,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64408,"mean_force":0.6061,"phase_index":2.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.50743,0.13082,0.14825]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50375,0.20562,0.29956]}],"total_contact_groups":13},"final_pose_error":0.04913,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50518,0.03359,0.02415],"final_tcp_position":[0.50261,0.18133,0.25463],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":883.05894,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":572.0,"n_steps_budget":1000.0,"object_pos_end":[0.50375,0.11174,0.03383],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":307.07648,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":601.0,"raw_peak_contact_force":414.20901,"subtask_id":"reach_approach","tcp_end":[0.5059,0.13492,0.05608],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.03219,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50579,0.03363,0.02415],"object_pos_start":[0.50375,0.11174,0.03383],"object_to_goal_dist_end":0.11487,"object_to_goal_dist_start":0.19188,"object_z_max":0.04077,"peak_contact_force":584.70259,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2478.0,"raw_peak_contact_force":654.66121,"subtask_id":"push_to_goal","tcp_end":[0.51333,0.08408,0.05209],"tcp_start":[0.5059,0.13492,0.05608],"tcp_to_object_dist_end":0.05817,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":239.0,"n_steps_budget":900.0,"object_pos_end":[0.50518,0.03359,0.02415],"object_pos_start":[0.50579,0.03363,0.02415],"object_to_goal_dist_end":0.1148,"object_to_goal_dist_start":0.11487,"object_z_max":0.02415,"peak_contact_force":0.64359,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":253.0,"raw_peak_contact_force":883.05894,"tcp_end":[0.50261,0.18133,0.25463],"tcp_start":[0.51333,0.08408,0.05209],"tcp_to_object_dist_end":0.27378,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```