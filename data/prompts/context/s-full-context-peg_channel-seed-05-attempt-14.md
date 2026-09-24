## Search State

- **Seed**: 5
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11 | -0.2281 | 0.06 | ❌ rejected |
| 13 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | -0.4192 | 0.00 | ❌ rejected |
| 12 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.0626 | 0.00 | ❌ rejected |
| 11 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | 0.0019 | 0.30 | ✅ accepted |
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | 0.0085 | 0.29 | ✅ accepted |

**Proposal policy**: task_score is 0.06 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.228) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_approach
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.08
  weight: 0.3
- id: push_to_goal
  target_entity: object
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
    - 0.03
    - 0.08
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
  subtask_id: reach_approach
- id: descend_to_peg
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_force_threshold:
      type: scalar
      range:
      - 2.0
      - 15.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
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
      - 10.0
      - 25.0
      default: 15.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_force_limit:
      type: scalar
      range:
      - 40.0
      - 50.0
      default: 45.0
      binds_to:
      - path: guards.push_force_guard.threshold
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
  guards:
  - id: push_force_guard
    when: during_phase
    predicate: force_below
    threshold: 45.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.01
    - 0.0
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
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, 0.08], tolerance=0.02
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tol: status=consumed; consumers=termination.pose_tolerance (replace)
- **descend_to_peg** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push_channel** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.2, mode=replace_offset_projection, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_duration: status=consumed; consumers=duration.max_time (replace)
    - push_force_limit: status=consumed; consumers=guards.push_force_guard.threshold (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=push_force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=45.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.01, 0.0, 0.0]
- **retract_away** (`retract`)
  - target: source=yaml, anchor=world, offset=[0.5, 0.2, 0.3], tolerance=0.05
  - orientation: mode=none
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)
    - retract_tol: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: -0.228
- **task_score** (E): 0.056
- **fitness_score**: 0.132  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.610

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.2128 |
| contact_peg_side | 1.00 | 1.00 | 0.0427 |
| push_channel | 0.00 | 1.00 | 0.0001 |
| retract_away | 1.00 | 1.00 | 0.2128 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.136, 0.098) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.557 | 2.488 |
| contact_peg_side | contact | 1.00 / force_exceeded | (0.508, 0.136, 0.098)→(0.502, 0.119, 0.060) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 2.000 | 18.968 | 18.968 |
| push_channel | push | 0.00 / guard_failure | (0.501, 0.100, 0.058)→(0.501, 0.100, 0.058) | (0.504, 0.095, 0.034)→(0.503, 0.083, 0.033) | 0.175→0.163 | 1.00 / 2.000 | 71.419 | 71.419 |
| retract_away | retract | 1.00 / step_budget | (0.501, 0.100, 0.058)→(0.500, 0.183, 0.254) | (0.503, 0.083, 0.033)→(0.503, 0.082, 0.034) | 0.163→0.163 | 1.00 / 1.000 | 0.539 | 55.925 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.070
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.070
- phase_score: 0.194
- phase_breakdown.push_to_goal_score: 0.004
- phase_breakdown.reach_approach_score: 0.636

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.144
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.070
- **Median Q (composite search score)**: -0.227
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at upper bound**: push_channel.push_distance
- **Final σ (mean)**: 0.382


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82474,"average_solve_count":97.0,"average_success_count":97.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.11282,"approach_behind.approach_tol":0.03761,"contact_peg_side.contact_force_threshold":10.46465,"contact_peg_side.contact_speed":0.12468,"push_channel.push_distance":0.3,"push_channel.push_downward":-0.00888,"push_channel.push_duration":15.07817,"push_channel.push_force_limit":53.86261,"push_channel.push_speed":0.03249,"retract_away.retract_speed":0.25193,"retract_away.retract_tol":0.06502},"optimized_scores":{"best_composite_score":-0.2414,"best_fitness_score":0.1186,"best_task_score":0.04476},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":280.0,"contact_point_centroid":[0.51323,0.0997,0.00907],"force_p95":52.9916,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":67.20824,"mean_force":42.34431,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50462,0.11715,0.05823]},{"body_a":"attachment","body_b":"peg","contact_count":280.0,"contact_point_centroid":[0.51512,0.11179,0.05736],"force_p95":52.47934,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":66.58845,"mean_force":41.87405,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50462,0.11715,0.05823]},{"body_a":"peg","body_b":"channel_base_body","contact_count":214.0,"contact_point_centroid":[0.50071,0.09062,0.00947],"force_p95":0.95373,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":55.9659,"mean_force":1.53222,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.50208,0.14313,0.15128]},{"body_a":"attachment","body_b":"peg","contact_count":13.0,"contact_point_centroid":[0.51514,0.10284,0.05819],"force_p95":49.93419,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.3747,"mean_force":16.53977,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.50375,0.10613,0.05934]},{"body_a":"peg","body_b":"channel_base_body","contact_count":198.0,"contact_point_centroid":[0.50565,0.1046,0.00939],"force_p95":0.5755,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.95061,"mean_force":0.63424,"phase_index":1.0,"phase_name":"contact_peg_side","phase_type":"contact","tcp_position_centroid":[0.51149,0.13709,0.07838]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51413,0.12062,0.0588],"force_p95":17.53923,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.53923,"mean_force":17.53923,"phase_index":1.0,"phase_name":"contact_peg_side","phase_type":"contact","tcp_position_centroid":[0.50552,0.12887,0.06006]},{"body_a":"peg","body_b":"channel_base_body","contact_count":380.0,"contact_point_centroid":[0.50559,0.10459,0.00936],"force_p95":0.58308,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57611,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50857,0.17293,0.19483]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49966,0.19978,0.29454]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52501,0.08836,0.05857],"force_p95":0.0,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.5023,0.13095,0.11997]}],"total_contact_groups":9},"final_pose_error":0.04977,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50412,0.08926,0.034],"final_tcp_position":[0.50122,0.18315,0.25319],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":67.20824,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":407.0,"n_steps_budget":1000.0,"object_pos_end":[0.50585,0.10459,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18479,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.55073,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":412.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_approach","tcp_end":[0.51897,0.1452,0.09832],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07732,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":198.0,"n_steps_budget":600.0,"object_pos_end":[0.50584,0.10469,0.03384],"object_pos_start":[0.50585,0.10459,0.03384],"object_to_goal_dist_end":0.18489,"object_to_goal_dist_start":0.18479,"object_z_max":0.03384,"peak_contact_force":17.95061,"phase_name":"contact_peg_side","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":199.0,"raw_peak_contact_force":17.95061,"subtask_id":"reach_approach","tcp_end":[0.50548,0.12879,0.0599],"tcp_start":[0.51897,0.1452,0.09832],"tcp_to_object_dist_end":0.0355,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":280.0,"n_steps_budget":1000.0,"object_pos_end":[0.50409,0.08977,0.03298],"object_pos_start":[0.50584,0.10469,0.03384],"object_to_goal_dist_end":0.16997,"object_to_goal_dist_start":0.18489,"object_z_max":0.03393,"peak_contact_force":67.20824,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":560.0,"raw_peak_contact_force":67.20824,"subtask_id":"push_to_goal","tcp_end":[0.50483,0.10556,0.05804],"tcp_start":[0.50481,0.10563,0.05804],"tcp_to_object_dist_end":0.02963,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":214.0,"n_steps_budget":660.0,"object_pos_end":[0.50412,0.08926,0.034],"object_pos_start":[0.5041,0.08972,0.03298],"object_to_goal_dist_end":0.16942,"object_to_goal_dist_start":0.16991,"object_z_max":0.03744,"peak_contact_force":0.54578,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":230.0,"raw_peak_contact_force":55.9659,"subtask_id":"push_to_goal","tcp_end":[0.50122,0.18315,0.25319],"tcp_start":[0.50483,0.10556,0.05804],"tcp_to_object_dist_end":0.23847,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.05263,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.08818,"approach_behind.approach_tol":0.04014,"contact_peg_side.contact_force_threshold":5.84093,"contact_peg_side.contact_speed":0.10867,"push_channel.push_distance":0.23865,"push_channel.push_downward":-0.00803,"push_channel.push_duration":18.26912,"push_channel.push_force_limit":54.96579,"push_channel.push_speed":0.09089,"retract_away.retract_speed":0.17746,"retract_away.retract_tol":0.04668},"optimized_scores":{"best_composite_score":-0.21597,"best_fitness_score":0.14403,"best_task_score":0.06956},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":138.0,"contact_point_centroid":[0.50548,0.06133,0.00908],"force_p95":52.25076,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":68.00751,"mean_force":40.35544,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49774,0.08469,0.05851]},{"body_a":"attachment","body_b":"peg","contact_count":138.0,"contact_point_centroid":[0.50824,0.07944,0.05752],"force_p95":51.85334,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":67.44538,"mean_force":39.90491,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49774,0.08469,0.05851]},{"body_a":"peg","body_b":"channel_base_body","contact_count":233.0,"contact_point_centroid":[0.49936,0.05804,0.00943],"force_p95":0.91923,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":54.65286,"mean_force":1.1058,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49803,0.12578,0.1531]},{"body_a":"attachment","body_b":"peg","contact_count":12.0,"contact_point_centroid":[0.50872,0.07331,0.05781],"force_p95":39.9759,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.0371,"mean_force":11.15476,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49712,0.07571,0.05908]},{"body_a":"peg","body_b":"channel_base_body","contact_count":255.0,"contact_point_centroid":[0.50294,0.06732,0.00938],"force_p95":0.55061,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.15561,"mean_force":0.5961,"phase_index":1.0,"phase_name":"contact_peg_side","phase_type":"contact","tcp_position_centroid":[0.49804,0.1019,0.07707]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.5074,0.08489,0.0588],"force_p95":12.71235,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.71235,"mean_force":12.71235,"phase_index":1.0,"phase_name":"contact_peg_side","phase_type":"contact","tcp_position_centroid":[0.49856,0.09289,0.06015]},{"body_a":"peg","body_b":"channel_base_body","contact_count":427.0,"contact_point_centroid":[0.50311,0.06748,0.00933],"force_p95":0.571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56679,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49876,0.15752,0.19802]}],"total_contact_groups":7},"final_pose_error":0.0494,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.502,0.05633,0.03379],"final_tcp_position":[0.49986,0.17899,0.25529],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":68.00751,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":443.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54753,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":427.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_approach","tcp_end":[0.49987,0.11154,0.09732],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0774,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":255.0,"n_steps_budget":600.0,"object_pos_end":[0.503,0.06747,0.0338],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.14763,"object_to_goal_dist_start":0.14758,"object_z_max":0.0338,"peak_contact_force":13.15561,"phase_name":"contact_peg_side","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":256.0,"raw_peak_contact_force":13.15561,"subtask_id":"reach_approach","tcp_end":[0.49858,0.09283,0.06004],"tcp_start":[0.49987,0.11154,0.09732],"tcp_to_object_dist_end":0.03676,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":138.0,"n_steps_budget":1000.0,"object_pos_end":[0.50193,0.05691,0.03275],"object_pos_start":[0.503,0.06747,0.0338],"object_to_goal_dist_end":0.13712,"object_to_goal_dist_start":0.14763,"object_z_max":0.03398,"peak_contact_force":68.00751,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":276.0,"raw_peak_contact_force":68.00751,"subtask_id":"push_to_goal","tcp_end":[0.4977,0.07532,0.05805],"tcp_start":[0.49769,0.07542,0.05805],"tcp_to_object_dist_end":0.03157,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":233.0,"n_steps_budget":960.0,"object_pos_end":[0.502,0.05633,0.03379],"object_pos_start":[0.50195,0.05684,0.03275],"object_to_goal_dist_end":0.13649,"object_to_goal_dist_start":0.13704,"object_z_max":0.03719,"peak_contact_force":0.5268,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":245.0,"raw_peak_contact_force":54.65286,"subtask_id":"push_to_goal","tcp_end":[0.49986,0.17899,0.25529],"tcp_start":[0.4977,0.07532,0.05805],"tcp_to_object_dist_end":0.25321,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0,"average_solve_count":97.0,"average_success_count":97.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.11014,"approach_behind.approach_tol":0.02435,"contact_peg_side.contact_force_threshold":11.05062,"contact_peg_side.contact_speed":0.12594,"push_channel.push_distance":0.18213,"push_channel.push_downward":-0.00501,"push_channel.push_duration":23.10051,"push_channel.push_force_limit":54.86969,"push_channel.push_speed":0.09044,"retract_away.retract_speed":0.20152,"retract_away.retract_tol":0.0395},"optimized_scores":{"best_composite_score":-0.22696,"best_fitness_score":0.13304,"best_task_score":0.05497},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":128.0,"contact_point_centroid":[0.50765,0.10563,0.00913],"force_p95":51.49533,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":79.04043,"mean_force":40.58631,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49981,0.12831,0.05859]},{"body_a":"attachment","body_b":"peg","contact_count":128.0,"contact_point_centroid":[0.51058,0.12354,0.0576],"force_p95":51.06068,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":78.44554,"mean_force":40.13486,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49981,0.12831,0.05859]},{"body_a":"peg","body_b":"channel_base_body","contact_count":215.0,"contact_point_centroid":[0.49968,0.10279,0.00945],"force_p95":0.97749,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":57.15609,"mean_force":1.3071,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49907,0.15162,0.15143]},{"body_a":"attachment","body_b":"peg","contact_count":12.0,"contact_point_centroid":[0.51058,0.11771,0.05808],"force_p95":46.51683,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.54216,"mean_force":13.92194,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49899,0.12017,0.05929]},{"body_a":"peg","body_b":"channel_base_body","contact_count":215.0,"contact_point_centroid":[0.50367,0.11169,0.00942],"force_p95":0.59913,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.79703,"mean_force":0.66094,"phase_index":1.0,"phase_name":"contact_peg_side","phase_type":"contact","tcp_position_centroid":[0.50238,0.14359,0.07843]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51021,0.12859,0.05877],"force_p95":25.30708,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.30708,"mean_force":25.30708,"phase_index":1.0,"phase_name":"contact_peg_side","phase_type":"contact","tcp_position_centroid":[0.50071,0.13576,0.0602]},{"body_a":"peg","body_b":"channel_base_body","contact_count":374.0,"contact_point_centroid":[0.50353,0.11162,0.00936],"force_p95":0.62795,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56462,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.5021,0.17611,0.19576]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49973,0.19975,0.29832]}],"total_contact_groups":8},"final_pose_error":0.04923,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50254,0.10183,0.03384],"final_tcp_position":[0.50021,0.18556,0.25294],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":79.04043,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":396.0,"n_steps_budget":1000.0,"object_pos_end":[0.50373,0.11178,0.03393],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19191,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.57411,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":390.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_approach","tcp_end":[0.50616,0.15163,0.09888],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07623,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":215.0,"n_steps_budget":600.0,"object_pos_end":[0.50376,0.11177,0.03381],"object_pos_start":[0.50373,0.11178,0.03393],"object_to_goal_dist_end":0.19191,"object_to_goal_dist_start":0.19191,"object_z_max":0.03393,"peak_contact_force":25.79703,"phase_name":"contact_peg_side","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":216.0,"raw_peak_contact_force":25.79703,"subtask_id":"reach_approach","tcp_end":[0.5007,0.1357,0.06004],"tcp_start":[0.50616,0.15163,0.09888],"tcp_to_object_dist_end":0.03563,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":128.0,"n_steps_budget":1000.0,"object_pos_end":[0.50249,0.10236,0.033],"object_pos_start":[0.50376,0.11177,0.03381],"object_to_goal_dist_end":0.18251,"object_to_goal_dist_start":0.19191,"object_z_max":0.03387,"peak_contact_force":79.04043,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":256.0,"raw_peak_contact_force":79.04043,"subtask_id":"push_to_goal","tcp_end":[0.49974,0.12001,0.05825],"tcp_start":[0.49973,0.12011,0.05825],"tcp_to_object_dist_end":0.03093,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":215.0,"n_steps_budget":810.0,"object_pos_end":[0.50254,0.10183,0.03384],"object_pos_start":[0.5025,0.10228,0.03301],"object_to_goal_dist_end":0.18195,"object_to_goal_dist_start":0.18243,"object_z_max":0.03705,"peak_contact_force":0.54434,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":227.0,"raw_peak_contact_force":57.15609,"subtask_id":"push_to_goal","tcp_end":[0.50021,0.18556,0.25294],"tcp_start":[0.49974,0.12001,0.05825],"tcp_to_object_dist_end":0.23457,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```