## Search State

- **Seed**: 8
- **Iteration**: 8 / 15

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
- Frozen realised-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`
- Frozen object start: [0.48615778212844485, 0.11898214746703403, 0.04]
- Frozen task target: [0.48615778212844485, -0.04101785253296597, 0.04]
- Goal object position: (0.48615778212844485, -0.04101785253296597, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.48615778212844485, 0.11898214746703403, 0.04)
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
  frozen_object_start: [0.4862, 0.119, 0.04]
  frozen_task_target: [0.4862, -0.041, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.48615778212844485, 0.11898214746703403, 0.04]}
  frozen_targets: {'channel_exit': [0.48615778212844485, -0.04101785253296597, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e

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
| `object` | offset from object initial position (0.48615778212844485, 0.11898214746703403, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.48615778212844485, -0.04101785253296597, 0.04) | final destination targets |
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

## Current Skill (Q=0.044) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: approach_peg
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.0
  weight: 0.3
- id: push_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.05
    - 0.12
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_arc_height:
      type: scalar
      range:
      - 0.04
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.arc_height
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_peg
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.03
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_force_threshold:
      type: scalar
      range:
      - 3.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.04
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    descend_y_offset:
      type: scalar
      range:
      - 0.02
      - 0.04
      default: 0.03
      binds_to:
      - path: target.offset.y
        mode: replace
  subtask_id: approach_peg
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.03
    - 0.0
    offset_along_axis:
      distance: 0.18
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.16
      - 0.22
      default: 0.18
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.008
      - 0.02
      default: 0.012
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.02
      - 0.05
      default: 0.03
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: force_limit_guard
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.01
    - 0.0
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.12], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_arc_height: status=consumed; consumers=generator.arc_height (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_y_offset: status=consumed; consumers=target.offset.y (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, 0.0], offset_along_axis={axis=channel_axis, distance=0.18, mode=add_to_offset, sign=positive}, tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=force_limit_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.01, 0.0]

## Design Metrics

- **Composite score**: 0.044
- **task_score** (E): 0.245
- **fitness_score**: 0.524  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1557 |
| descend_1 | 1.00 | 1.00 | 0.1280 |
| push_1 | 0.00 | 1.00 | 0.0005 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.518, 0.128, 0.172) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.544 | 3.526 |
| descend_1 | descend | 1.00 / step_budget | (0.518, 0.128, 0.172)→(0.504, 0.107, 0.048) | (0.503, 0.080, 0.034)→(0.502, 0.072, 0.036) | 0.160→0.152 | 1.00 / 1.000 | 0.199 | 153.172 |
| push_1 | push | 0.00 / guard_failure | (0.500, 0.000, 0.037)→(0.500, -0.000, 0.037) | (0.502, 0.072, 0.036)→(0.505, -0.033, 0.033) | 0.152→0.051 | 1.00 / 2.333 | 30.201 | 66.356 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.867
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.311
- phase_score: 0.845
- phase_breakdown.approach_peg_score: 0.635
- phase_breakdown.push_to_goal_score: 0.935

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.631
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.311
- **Median Q (composite search score)**: 0.089
- **K-run variance**: 0.0124
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.258


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a8ce855c7f52ba2d198de8387bdd2f3b869655c206850d620daaec6ac6f298cd`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `79b30dd7102e96fb2fa0880d3932c959e04a6f943c7e87b878f77a0e54f87a94`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.8733,"average_solve_count":221.0,"average_success_count":221.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_arc_height":0.09175,"approach_1.approach_speed":0.10793,"descend_1.descend_speed":0.02388,"descend_1.descend_tolerance":0.01268,"descend_1.descend_y_offset":0.03084,"push_1.push_distance":0.17833,"push_1.push_force_guard_threshold":37.10609,"push_1.push_speed":0.01833,"push_1.push_tolerance":0.03351},"optimized_scores":{"best_composite_score":-0.10963,"best_fitness_score":0.37037,"best_task_score":0.20126},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":39.0,"contact_point_centroid":[0.49496,0.11016,0.04248],"force_p95":35.80359,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.68409,"mean_force":12.33991,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48969,0.12075,0.04135]},{"body_a":"peg","body_b":"channel_base_body","contact_count":55.0,"contact_point_centroid":[0.50008,0.08959,0.00958],"force_p95":34.41324,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.80385,"mean_force":7.47187,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48994,0.12741,0.04249]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":41.0,"contact_point_centroid":[0.52569,0.073,0.03671],"force_p95":15.70936,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.63498,"mean_force":3.4594,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49022,0.09962,0.0393]},{"body_a":"peg","body_b":"channel_base_body","contact_count":295.0,"contact_point_centroid":[0.49635,0.11906,0.00936],"force_p95":0.63739,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56991,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49124,0.22187,0.22392]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49976,0.20234,0.29759]},{"body_a":"peg","body_b":"channel_base_body","contact_count":322.0,"contact_point_centroid":[0.49597,0.11913,0.00944],"force_p95":0.59541,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66019,"mean_force":0.54075,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48669,0.1717,0.10598]}],"total_contact_groups":6},"final_pose_error":0.10443,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50624,0.05052,0.03721],"final_tcp_position":[0.49088,0.07514,0.0372],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":57.68409,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":320.0,"n_steps_budget":840.0,"object_pos_end":[0.49602,0.11911,0.03383],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19924,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.51749,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":319.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach_peg","tcp_end":[0.48444,0.18835,0.16263],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14668,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":322.0,"n_steps_budget":1000.0,"object_pos_end":[0.49605,0.11921,0.03396],"object_pos_start":[0.49602,0.11911,0.03383],"object_to_goal_dist_end":0.19934,"object_to_goal_dist_start":0.19924,"object_z_max":0.034,"peak_contact_force":0.51975,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":322.0,"raw_peak_contact_force":0.66019,"subtask_id":"approach_peg","tcp_end":[0.49099,0.15432,0.04716],"tcp_start":[0.48444,0.18835,0.16263],"tcp_to_object_dist_end":0.03785,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":117.0,"n_steps_budget":1000.0,"object_pos_end":[0.50583,0.05133,0.03674],"object_pos_start":[0.49605,0.11921,0.03396],"object_to_goal_dist_end":0.1315,"object_to_goal_dist_start":0.19934,"object_z_max":0.04098,"peak_contact_force":1.44783,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":135.0,"raw_peak_contact_force":57.68409,"subtask_id":"push_to_goal","tcp_end":[0.49088,0.07514,0.0372],"tcp_start":[0.49084,0.07565,0.03726],"tcp_to_object_dist_end":0.02812,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `0a7722137b05abd45e72adac5a0a8f18d70c24ddc36cf4c70c52ed7e5618005d`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.8502,"average_solve_count":247.0,"average_success_count":247.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_arc_height":0.10171,"approach_1.approach_speed":0.09871,"descend_1.descend_speed":0.01793,"descend_1.descend_tolerance":0.00918,"descend_1.descend_y_offset":0.02109,"push_1.push_distance":0.21118,"push_1.push_force_guard_threshold":34.82765,"push_1.push_speed":0.01841,"push_1.push_tolerance":0.03205},"optimized_scores":{"best_composite_score":0.15129,"best_fitness_score":0.63129,"best_task_score":0.31065},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":350.0,"contact_point_centroid":[0.50737,0.06376,0.00928],"force_p95":137.76385,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":161.6006,"mean_force":15.42209,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51764,0.09344,0.10946]},{"body_a":"attachment","body_b":"peg","contact_count":45.0,"contact_point_centroid":[0.51548,0.07768,0.05539],"force_p95":160.98325,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":161.16219,"mean_force":115.82179,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50913,0.08697,0.05485]},{"body_a":"peg","body_b":"channel_base_body","contact_count":6.0,"contact_point_centroid":[0.50085,-0.10135,0.02282],"force_p95":75.10308,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":76.51759,"mean_force":35.15923,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50468,-0.03392,0.03756]},{"body_a":"attachment","body_b":"peg","contact_count":85.0,"contact_point_centroid":[0.50528,-0.00702,0.0439],"force_p95":13.82866,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":75.20542,"mean_force":4.24049,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50545,0.00445,0.03966]},{"body_a":"peg","body_b":"channel_base_body","contact_count":59.0,"contact_point_centroid":[0.49828,-0.01131,0.00887],"force_p95":12.79869,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.03277,"mean_force":2.87354,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50651,0.04681,0.04264]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":9.0,"contact_point_centroid":[0.47467,-0.04474,0.03635],"force_p95":8.82627,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.13237,"mean_force":4.67455,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50558,0.01169,0.04006]},{"body_a":"peg","body_b":"channel_base_body","contact_count":387.0,"contact_point_centroid":[0.50559,0.06304,0.00935],"force_p95":0.5838,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.58152,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52408,0.12409,0.25997]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50102,0.1946,0.30026]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,0.06253,0.05668],"force_p95":0.41485,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41485,"mean_force":0.41485,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51026,0.08689,0.05244]}],"total_contact_groups":9},"final_pose_error":0.09339,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5041,-0.07573,0.03441],"final_tcp_position":[0.5046,-0.03615,0.03743],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":161.6006,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":415.0,"n_steps_budget":1000.0,"object_pos_end":[0.50603,0.06301,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14327,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.5479,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":421.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach_peg","tcp_end":[0.53101,0.10129,0.17612],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14947,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":350.0,"n_steps_budget":1000.0,"object_pos_end":[0.50526,0.05165,0.03762],"object_pos_start":[0.50603,0.06301,0.0338],"object_to_goal_dist_end":0.13177,"object_to_goal_dist_start":0.14327,"object_z_max":0.03705,"peak_contact_force":0.04681,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":396.0,"raw_peak_contact_force":161.6006,"subtask_id":"approach_peg","tcp_end":[0.50933,0.08648,0.04793],"tcp_start":[0.53101,0.10129,0.17612],"tcp_to_object_dist_end":0.03656,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":170.0,"n_steps_budget":1000.0,"object_pos_end":[0.50411,-0.07513,0.0343],"object_pos_start":[0.50526,0.05165,0.03762],"object_to_goal_dist_end":0.00855,"object_to_goal_dist_start":0.13177,"object_z_max":0.0416,"peak_contact_force":55.96884,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":159.0,"raw_peak_contact_force":76.51759,"subtask_id":"push_to_goal","tcp_end":[0.5046,-0.03615,0.03743],"tcp_start":[0.50464,-0.0357,0.03747],"tcp_to_object_dist_end":0.03911,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `bf9c239495ea25cc1b534d0795871edaef0fee72244885088104a44eb548c1a2`; realized-scene SHA-256: `11c1f773d01ee1d435c5ecc0d1531095d6f84a2c0ab26c3ff2560d4c62fcd41a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53648,0.05661,0.04]},{"name":"goal","value":[0.53648,-0.10339,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,0.05661,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53648,-0.10339,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.95868,"average_solve_count":242.0,"average_success_count":242.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_arc_height":0.1006,"approach_1.approach_speed":0.1144,"descend_1.descend_speed":0.02443,"descend_1.descend_tolerance":0.01891,"descend_1.descend_y_offset":0.02021,"push_1.push_distance":0.2118,"push_1.push_force_guard_threshold":42.60864,"push_1.push_speed":0.02686,"push_1.push_tolerance":0.0358},"optimized_scores":{"best_composite_score":0.08914,"best_fitness_score":0.56914,"best_task_score":0.22406},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52505,0.07953,0.05999],"force_p95":292.08408,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":297.25458,"mean_force":203.07382,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51182,0.07962,0.05097]},{"body_a":"peg","body_b":"channel_base_body","contact_count":357.0,"contact_point_centroid":[0.50747,0.05747,0.00923],"force_p95":142.75007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":165.39092,"mean_force":17.68963,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52159,0.08676,0.10822]},{"body_a":"attachment","body_b":"peg","contact_count":53.0,"contact_point_centroid":[0.51644,0.07017,0.05491],"force_p95":161.19433,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":164.86597,"mean_force":115.57686,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51064,0.07982,0.05418]},{"body_a":"attachment","body_b":"peg","contact_count":64.0,"contact_point_centroid":[0.50415,-0.00867,0.04071],"force_p95":28.60662,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":64.86622,"mean_force":5.63047,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50584,0.00268,0.03962]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50936,-0.10051,0.04489],"force_p95":55.61927,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":55.70155,"mean_force":47.92205,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5046,-0.03858,0.03738]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":13.0,"contact_point_centroid":[0.4749,-0.0369,0.03524],"force_p95":20.1752,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.68752,"mean_force":6.95948,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50657,0.02462,0.04116]},{"body_a":"peg","body_b":"channel_base_body","contact_count":72.0,"contact_point_centroid":[0.49866,-0.02703,0.00906],"force_p95":14.26933,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.37768,"mean_force":3.48852,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50662,0.0225,0.04111]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":20.0,"contact_point_centroid":[0.52537,0.02469,0.03879],"force_p95":2.4751,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.38195,"mean_force":1.24257,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50726,0.04857,0.04247]},{"body_a":"peg","body_b":"channel_base_body","contact_count":395.0,"contact_point_centroid":[0.50576,0.05661,0.00934],"force_p95":0.60202,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.58677,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52927,0.12065,0.26332]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50145,0.19405,0.30078]}],"total_contact_groups":10},"final_pose_error":0.09704,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50534,-0.07584,0.02921],"final_tcp_position":[0.50449,-0.03972,0.03727],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":297.25458,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":424.0,"n_steps_budget":960.0,"object_pos_end":[0.50615,0.05661,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13689,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.56802,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":432.0,"raw_peak_contact_force":4.44541,"subtask_id":"approach_peg","tcp_end":[0.53834,0.0953,0.17615],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.151,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":357.0,"n_steps_budget":1000.0,"object_pos_end":[0.50402,0.04505,0.03738],"object_pos_start":[0.50615,0.05661,0.03378],"object_to_goal_dist_end":0.12514,"object_to_goal_dist_start":0.13689,"object_z_max":0.03674,"peak_contact_force":0.02983,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":416.0,"raw_peak_contact_force":297.25458,"subtask_id":"approach_peg","tcp_end":[0.51047,0.07963,0.04752],"tcp_start":[0.53834,0.0953,0.17615],"tcp_to_object_dist_end":0.03661,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":166.0,"n_steps_budget":1000.0,"object_pos_end":[0.50529,-0.07476,0.02943],"object_pos_start":[0.50402,0.04505,0.03738],"object_to_goal_dist_end":0.01292,"object_to_goal_dist_start":0.12514,"object_z_max":0.04226,"peak_contact_force":33.18589,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":172.0,"raw_peak_contact_force":64.86622,"subtask_id":"push_to_goal","tcp_end":[0.50449,-0.03972,0.03727],"tcp_start":[0.50456,-0.03924,0.03733],"tcp_to_object_dist_end":0.03592,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```