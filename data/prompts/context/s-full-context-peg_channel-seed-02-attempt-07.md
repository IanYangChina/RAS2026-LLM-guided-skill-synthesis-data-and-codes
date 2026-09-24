## Search State

- **Seed**: 2
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | 0.0610 | 0.41 | ✅ accepted |
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 8 | 0.1209 | 0.27 | ❌ rejected |
| 5 | approach → descend → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.0672 | 0.34 | ✅ accepted |
| 4 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 6 | 0.2158 | 0.27 | ❌ rejected |
| 3 | approach → descend → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.0632 | 0.31 | ✅ accepted |

**Proposal policy**: task_score is 0.41 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.061) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: approach_peg
  anchor: object
  offset:
  - 0.0
  - 0.02
  - 0.06
  weight: 0.3
- id: push_through
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_peg
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
    - 0.06
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
    approach_y_offset:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.y
        mode: replace
  subtask_id: approach_peg
- id: descend_to_contact
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
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    descend_y_offset:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.y
        mode: replace
  subtask_id: approach_peg
- id: lateral_align
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.02
    - 0.0
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - -1.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.05
  parameters:
    align_x_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    align_y_offset:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.y
        mode: replace
  subtask_id: push_through
- id: push_channel
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.18
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - -1.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.05
  parameters:
    guard_force_threshold:
      type: scalar
      range:
      - 30.0
      - 40.0
      default: 38.0
      binds_to:
      - path: guards.push_force_guard.threshold
        mode: replace
    max_push_duration:
      type: scalar
      range:
      - 1.0
      - 5.0
      default: 3.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.12
      - 0.22
      default: 0.18
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    retry_y_offset:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: -0.015
      binds_to:
      - path: retry.offset.y
        mode: replace
  guards:
  - id: push_force_guard
    when: during_phase
    predicate: force_below
    threshold: 38.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - -0.015
    - 0.0
  subtask_id: push_through

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.02, 0.06]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_y_offset: status=consumed; consumers=target.offset.y (replace)
- **descend_to_contact** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.02, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_y_offset: status=consumed; consumers=target.offset.y (replace)
- **lateral_align** (`align`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.02, 0.0]
  - orientation: mode=align_axis, axis=[0.0, -1.0, 0.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - align_x_offset: status=consumed; consumers=target.offset.x (replace)
    - align_y_offset: status=consumed; consumers=target.offset.y (replace)
- **push_channel** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.18, mode=add_to_offset, sign=positive}
  - orientation: mode=align_axis, axis=[0.0, -1.0, 0.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - guard_force_threshold: status=consumed; consumers=guards.push_force_guard.threshold (replace)
    - max_push_duration: status=consumed; consumers=duration.max_time (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - retry_y_offset: status=consumed; consumers=retry.offset.y (replace)
  - guards:
    - id=push_force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=38.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, -0.015, 0.0]

## Design Metrics

- **Composite score**: 0.061
- **task_score** (E): 0.410
- **fitness_score**: 0.621  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.560

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1992 |
| descend_to_contact | 1.00 | 1.00 | 0.0829 |
| lateral_align | 1.00 | 1.00 | 0.0197 |
| push_channel | 0.33 | 1.00 | 0.0534 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.492, 0.096, 0.132) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.544 | 3.659 |
| descend_to_contact | descend | 1.00 / step_budget | (0.492, 0.096, 0.132)→(0.500, 0.088, 0.053) | (0.498, 0.068, 0.034)→(0.500, 0.067, 0.032) | 0.148→0.147 | 1.00 / 2.667 | 283.921 | 367.270 |
| lateral_align | align | 1.00 / step_budget | (0.500, 0.088, 0.053)→(0.507, 0.094, 0.038) | (0.500, 0.067, 0.032)→(0.494, 0.061, 0.035) | 0.147→0.142 | 1.00 / 1.667 | 102.320 | 422.940 |
| push_channel | push | 0.33 / guard_failure | (0.501, -0.003, 0.036)→(0.499, -0.056, 0.035) | (0.494, 0.061, 0.035)→(0.499, -0.085, 0.036) | 0.142→0.009 | 1.00 / 2.667 | 20.532 | 36.623 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.936
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.652
- phase_score: 0.748
- phase_breakdown.approach_peg_score: 0.327
- phase_breakdown.push_through_score: 0.928

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.710
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.652
- **Median Q (composite search score)**: 0.021
- **K-run variance**: 0.0039
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.376


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.66393,"average_solve_count":122.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.09365,"approach_peg.approach_y_offset":0.02624,"descend_to_contact.descend_y_offset":0.01108,"lateral_align.align_x_offset":0.01272,"lateral_align.align_y_offset":0.02101,"push_channel.guard_force_threshold":35.04461,"push_channel.max_push_duration":2.73931,"push_channel.push_distance":0.14968,"push_channel.push_speed":0.0904,"push_channel.retry_y_offset":-0.01552},"optimized_scores":{"best_composite_score":0.14965,"best_fitness_score":0.70965,"best_task_score":0.65221},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":237.0,"contact_point_centroid":[0.52513,0.08087,0.05999],"force_p95":392.86991,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":509.8439,"mean_force":345.67121,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.51196,0.08091,0.0477]},{"body_a":"peg","body_b":"channel_base_body","contact_count":382.0,"contact_point_centroid":[0.49949,0.06729,0.00909],"force_p95":198.28804,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":205.04922,"mean_force":43.14305,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.48554,0.08617,0.08707]},{"body_a":"attachment","body_b":"peg","contact_count":107.0,"contact_point_centroid":[0.50579,0.07707,0.05414],"force_p95":198.55529,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":204.52849,"mean_force":152.13209,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.4941,0.07927,0.05317]},{"body_a":"peg","body_b":"channel_base_body","contact_count":297.0,"contact_point_centroid":[0.51375,0.06863,0.00756],"force_p95":192.80386,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":194.42768,"mean_force":170.62327,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.51103,0.08062,0.04784]},{"body_a":"attachment","body_b":"peg","contact_count":285.0,"contact_point_centroid":[0.51648,0.07056,0.05124],"force_p95":192.33444,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":193.855,"mean_force":177.28317,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.51104,0.08053,0.04804]},{"body_a":"peg","body_b":"channel_base_body","contact_count":49.0,"contact_point_centroid":[0.4928,-0.10083,0.03163],"force_p95":33.07883,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.807,"mean_force":19.87791,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49899,-0.05464,0.03618]},{"body_a":"attachment","body_b":"peg","contact_count":609.0,"contact_point_centroid":[0.49904,0.00024,0.03761],"force_p95":21.86865,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.56998,"mean_force":3.95491,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50294,0.01138,0.03677]},{"body_a":"peg","body_b":"channel_base_body","contact_count":601.0,"contact_point_centroid":[0.49469,-0.02332,0.00985],"force_p95":7.48303,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.85819,"mean_force":2.27875,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50322,0.01548,0.03686]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":718.0,"contact_point_centroid":[0.47481,-0.00284,0.03193],"force_p95":5.63848,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.85022,"mean_force":1.27946,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50378,0.02477,0.03691]},{"body_a":"peg","body_b":"channel_base_body","contact_count":573.0,"contact_point_centroid":[0.49532,0.06382,0.00937],"force_p95":0.57978,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56038,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48855,0.14655,0.21581]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":12.0,"contact_point_centroid":[0.47412,0.05753,0.0569],"force_p95":1.47126,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.67425,"mean_force":0.51191,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.51094,0.0826,0.04316]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49929,0.19818,0.29722]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52501,0.08314,0.06],"force_p95":0.0,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51075,0.08317,0.04169]}],"total_contact_groups":13},"final_pose_error":0.03448,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49316,-0.08595,0.03566],"final_tcp_position":[0.49883,-0.05713,0.03605],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":509.8439,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":600.0,"n_steps_budget":1000.0,"object_pos_end":[0.49526,0.06374,0.03395],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14394,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54171,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":601.0,"raw_peak_contact_force":2.44546,"subtask_id":"approach_peg","tcp_end":[0.47931,0.09695,0.14043],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11267,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":382.0,"n_steps_budget":690.0,"object_pos_end":[0.50122,0.06267,0.03051],"object_pos_start":[0.49526,0.06374,0.03395],"object_to_goal_dist_end":0.143,"object_to_goal_dist_start":0.14394,"object_z_max":0.034,"peak_contact_force":196.48952,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":489.0,"raw_peak_contact_force":205.04922,"subtask_id":"approach_peg","tcp_end":[0.50171,0.07827,0.0484],"tcp_start":[0.47931,0.09695,0.14043],"tcp_to_object_dist_end":0.02374,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":297.0,"n_steps_budget":600.0,"object_pos_end":[0.49251,0.05802,0.03341],"object_pos_start":[0.50122,0.06267,0.03051],"object_to_goal_dist_end":0.13838,"object_to_goal_dist_start":0.143,"object_z_max":0.03335,"peak_contact_force":305.95009,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":831.0,"raw_peak_contact_force":509.8439,"subtask_id":"push_through","tcp_end":[0.51075,0.08317,0.04169],"tcp_start":[0.50171,0.07827,0.0484],"tcp_to_object_dist_end":0.03215,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":967.0,"n_steps_budget":1000.0,"object_pos_end":[0.4932,-0.08578,0.03571],"object_pos_start":[0.49251,0.05802,0.03341],"object_to_goal_dist_end":0.00991,"object_to_goal_dist_start":0.13838,"object_z_max":0.03597,"peak_contact_force":30.79968,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1978.0,"raw_peak_contact_force":37.807,"subtask_id":"push_through","tcp_end":[0.49883,-0.05713,0.03605],"tcp_start":[0.49886,-0.0571,0.03609],"tcp_to_object_dist_end":0.0292,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75,"average_solve_count":124.0,"average_success_count":124.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.08369,"approach_peg.approach_y_offset":0.02304,"descend_to_contact.descend_y_offset":0.02733,"lateral_align.align_x_offset":0.01998,"lateral_align.align_y_offset":0.0372,"push_channel.guard_force_threshold":39.97961,"push_channel.max_push_duration":3.36015,"push_channel.push_distance":0.19405,"push_channel.push_speed":0.09417,"push_channel.retry_y_offset":-0.00806},"optimized_scores":{"best_composite_score":0.01211,"best_fitness_score":0.57211,"best_task_score":0.27085},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":117.0,"contact_point_centroid":[0.47497,0.08666,0.05984],"force_p95":465.28688,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":503.88535,"mean_force":400.15344,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.48462,0.08677,0.05803]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.475,0.09035,0.05999],"force_p95":406.84314,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":410.61383,"mean_force":331.80448,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.48629,0.08707,0.05772]},{"body_a":"peg","body_b":"channel_base_body","contact_count":51.0,"contact_point_centroid":[0.4963,-0.10103,0.04325],"force_p95":34.22564,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.75964,"mean_force":25.74073,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49922,-0.05465,0.03505]},{"body_a":"attachment","body_b":"peg","contact_count":668.0,"contact_point_centroid":[0.49827,0.00318,0.03337],"force_p95":21.84106,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.43383,"mean_force":2.96745,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50005,0.01492,0.03292]},{"body_a":"attachment","body_b":"peg","contact_count":84.0,"contact_point_centroid":[0.48894,0.07544,0.0599],"force_p95":1.49981,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.19729,"mean_force":0.99765,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.48484,0.08679,0.05803]},{"body_a":"peg","body_b":"channel_base_body","contact_count":747.0,"contact_point_centroid":[0.49445,-0.01449,0.00982],"force_p95":3.61178,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.84256,"mean_force":1.40149,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5003,0.0225,0.03287]},{"body_a":"peg","body_b":"channel_base_body","contact_count":382.0,"contact_point_centroid":[0.49625,0.05448,0.00949],"force_p95":1.47271,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.83697,"mean_force":0.72653,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.47656,0.08733,0.08324]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":126.0,"contact_point_centroid":[0.47491,-0.05412,0.0337],"force_p95":1.29183,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.9661,"mean_force":0.5766,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49954,-0.02501,0.03417]},{"body_a":"peg","body_b":"channel_base_body","contact_count":168.0,"contact_point_centroid":[0.49517,0.05642,0.0095],"force_p95":0.57722,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.19458,"mean_force":0.5956,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.49508,0.08999,0.04546]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.4909,0.07593,0.05992],"force_p95":3.99758,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.8619,"mean_force":1.13144,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.48767,0.08762,0.05573]},{"body_a":"peg","body_b":"channel_base_body","contact_count":613.0,"contact_point_centroid":[0.49442,0.059,0.00936],"force_p95":0.56306,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.57007,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48165,0.14221,0.21047]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49889,0.19762,0.2962]}],"total_contact_groups":12},"final_pose_error":0.07864,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49604,-0.08626,0.03518],"final_tcp_position":[0.49924,-0.05717,0.03507],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":503.88535,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":642.0,"n_steps_budget":1000.0,"object_pos_end":[0.49403,0.05906,0.03388],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13932,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54533,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":648.0,"raw_peak_contact_force":4.20518,"subtask_id":"approach_peg","tcp_end":[0.46606,0.08895,0.13072],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10513,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":382.0,"n_steps_budget":660.0,"object_pos_end":[0.49443,0.05822,0.03517],"object_pos_start":[0.49403,0.05906,0.03388],"object_to_goal_dist_end":0.13841,"object_to_goal_dist_start":0.13932,"object_z_max":0.03517,"peak_contact_force":336.92081,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":583.0,"raw_peak_contact_force":503.88535,"subtask_id":"approach_peg","tcp_end":[0.48609,0.08685,0.05775],"tcp_start":[0.46606,0.08895,0.13072],"tcp_to_object_dist_end":0.03741,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":168.0,"n_steps_budget":600.0,"object_pos_end":[0.49436,0.05829,0.03385],"object_pos_start":[0.49443,0.05822,0.03517],"object_to_goal_dist_end":0.13855,"object_to_goal_dist_start":0.13841,"object_z_max":0.03528,"peak_contact_force":0.54224,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":181.0,"raw_peak_contact_force":410.61383,"subtask_id":"push_through","tcp_end":[0.50481,0.09293,0.03504],"tcp_start":[0.48609,0.08685,0.05775],"tcp_to_object_dist_end":0.0362,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":996.0,"n_steps_budget":1000.0,"object_pos_end":[0.49609,-0.08613,0.03521],"object_pos_start":[0.49436,0.05829,0.03385],"object_to_goal_dist_end":0.00871,"object_to_goal_dist_start":0.13855,"object_z_max":0.03587,"peak_contact_force":1.49308,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1592.0,"raw_peak_contact_force":42.75964,"subtask_id":"push_through","tcp_end":[0.49924,-0.05717,0.03507],"tcp_start":[0.49926,-0.05714,0.0351],"tcp_to_object_dist_end":0.02913,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71667,"average_solve_count":120.0,"average_success_count":120.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.08032,"approach_peg.approach_y_offset":0.01688,"descend_to_contact.descend_y_offset":0.01554,"lateral_align.align_x_offset":0.0011,"lateral_align.align_y_offset":0.03265,"push_channel.guard_force_threshold":35.2261,"push_channel.max_push_duration":2.07068,"push_channel.push_distance":0.18285,"push_channel.push_speed":0.09932,"push_channel.retry_y_offset":0.00837},"optimized_scores":{"best_composite_score":0.02124,"best_fitness_score":0.58124,"best_task_score":0.30796},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":61.0,"contact_point_centroid":[0.52511,0.09857,0.05999],"force_p95":367.81322,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":392.87624,"mean_force":308.32775,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51221,0.09867,0.05269]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":91.0,"contact_point_centroid":[0.52509,0.09922,0.05999],"force_p95":310.07691,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":348.36203,"mean_force":247.18505,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.51208,0.09928,0.05092]},{"body_a":"peg","body_b":"channel_base_body","contact_count":141.0,"contact_point_centroid":[0.50715,0.07952,0.00844],"force_p95":157.05107,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":157.70096,"mean_force":93.44722,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.51104,0.10054,0.04857]},{"body_a":"attachment","body_b":"peg","contact_count":101.0,"contact_point_centroid":[0.51606,0.08901,0.0528],"force_p95":156.72426,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":157.21273,"mean_force":129.82892,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.51202,0.09939,0.05077]},{"body_a":"peg","body_b":"channel_base_body","contact_count":301.0,"contact_point_centroid":[0.51014,0.08373,0.00908],"force_p95":131.56022,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":136.26757,"mean_force":40.16751,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51725,0.09992,0.08033]},{"body_a":"attachment","body_b":"peg","contact_count":101.0,"contact_point_centroid":[0.52047,0.09035,0.05494],"force_p95":133.06875,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":135.76032,"mean_force":118.14185,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51177,0.09844,0.05414]},{"body_a":"attachment","body_b":"peg","contact_count":683.0,"contact_point_centroid":[0.50145,0.00776,0.03965],"force_p95":6.95302,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.3021,"mean_force":2.1793,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50039,0.01937,0.03422]},{"body_a":"peg","body_b":"channel_base_body","contact_count":16.0,"contact_point_centroid":[0.50654,-0.10039,0.0596],"force_p95":18.6702,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.57319,"mean_force":11.43626,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49853,-0.053,0.03492]},{"body_a":"peg","body_b":"channel_base_body","contact_count":633.0,"contact_point_centroid":[0.49997,-0.00901,0.00986],"force_p95":7.09608,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.72542,"mean_force":2.37962,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50079,0.03159,0.03421]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":287.0,"contact_point_centroid":[0.52509,-0.04566,0.02539],"force_p95":3.20095,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.05571,"mean_force":0.99457,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49943,-0.01698,0.03458]},{"body_a":"peg","body_b":"channel_base_body","contact_count":625.0,"contact_point_centroid":[0.50574,0.08091,0.00936],"force_p95":0.55661,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.57118,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51467,0.14975,0.20823]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50009,0.19785,0.29601]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":154.0,"contact_point_centroid":[0.47492,0.04626,0.02803],"force_p95":1.27265,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.09437,"mean_force":0.46585,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50176,0.07498,0.03354]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":7.0,"contact_point_centroid":[0.47488,0.0668,0.05997],"force_p95":0.73965,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.81834,"mean_force":0.37988,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.5095,0.10252,0.04505]}],"total_contact_groups":14},"final_pose_error":0.06138,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50689,-0.08196,0.0356],"final_tcp_position":[0.49843,-0.05391,0.03485],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":392.87624,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":654.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54458,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":661.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach_peg","tcp_end":[0.52995,0.10346,0.12613],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09805,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":301.0,"n_steps_budget":630.0,"object_pos_end":[0.50411,0.08024,0.03099],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.16055,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":318.35146,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":463.0,"raw_peak_contact_force":392.87624,"subtask_id":"approach_peg","tcp_end":[0.51214,0.09897,0.05205],"tcp_start":[0.52995,0.10346,0.12613],"tcp_to_object_dist_end":0.02931,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":143.0,"n_steps_budget":600.0,"object_pos_end":[0.49613,0.06779,0.03881],"object_pos_start":[0.50411,0.08024,0.03099],"object_to_goal_dist_end":0.14784,"object_to_goal_dist_start":0.16055,"object_z_max":0.03883,"peak_contact_force":0.4682,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":340.0,"raw_peak_contact_force":348.36203,"subtask_id":"push_through","tcp_end":[0.50624,0.10589,0.0378],"tcp_start":[0.51214,0.09897,0.05205],"tcp_to_object_dist_end":0.03943,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50689,-0.08196,0.0356],"object_pos_start":[0.49613,0.06779,0.03881],"object_to_goal_dist_end":0.00841,"object_to_goal_dist_start":0.14784,"object_z_max":0.03881,"peak_contact_force":29.3021,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1773.0,"raw_peak_contact_force":29.3021,"subtask_id":"push_through","tcp_end":[0.49843,-0.05391,0.03485],"tcp_start":[0.50624,0.10589,0.0378],"tcp_to_object_dist_end":0.0293,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```