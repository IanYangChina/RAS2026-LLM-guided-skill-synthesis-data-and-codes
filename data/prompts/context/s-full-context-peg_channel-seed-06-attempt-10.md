## Search State

- **Seed**: 6
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 11 | -0.0749 | 0.14 | ❌ rejected |
| 9 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 9 | 0.0239 | 0.10 | ❌ rejected |
| 8 | approach → descend → align → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 16 | -0.6792 | 0.00 | ❌ rejected |
| 7 | approach → descend → align → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 17 | -0.6617 | 0.04 | ❌ rejected |
| 6 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 10 | 0.0600 | 0.36 | ❌ rejected |

**Proposal policy**: task_score is 0.14 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
| `object` | offset from object initial position (0.5030531481177555, 0.06746166958506708, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5030531481177555, -0.09253833041493292, 0.04) | final destination targets |
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

## Current Skill (Q=-0.075) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: behind_peg
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.1
  weight: 0.3
- id: insertion_progress
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach
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
    - 0.05
    - 0.1
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.001
      - 0.01
      default: 0.005
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: behind_peg
- id: descend
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.05
    - 0.0
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    descend_tolerance:
      type: scalar
      range:
      - 0.001
      - 0.01
      default: 0.005
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    descend_z_offset:
      type: scalar
      range:
      - -0.01
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: add
- id: contact_seating
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    entity: channel_exit
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 2.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.015
      binds_to:
      - path: generator.speed
        mode: replace
- id: push
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_goal
    entity: channel_exit
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    push_max_time:
      type: scalar
      range:
      - 2.0
      - 8.0
      default: 5.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.005
      - 0.04
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 39.0
    on_failure: retry
  retries:
    max_attempts: 3
    strategy: reduce_speed
  subtask_id: insertion_progress

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.1]
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **descend** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.0]
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - descend_z_offset: status=consumed; consumers=target.offset.z (add)
- **contact_seating** (`contact`)
  - target: source=yaml, anchor=task_goal, entity=channel_exit, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **push** (`push`)
  - target: source=yaml, anchor=task_goal, entity=channel_exit, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - push_max_time: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=39.0
  - retries: max_attempts=3, strategy=reduce_speed

## Design Metrics

- **Composite score**: -0.075
- **task_score** (E): 0.141
- **fitness_score**: 0.257  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.278
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.610

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.1254 |
| descend | 1.00 | 1.00 | 0.1496 |
| contact | 1.00 | 1.00 | 0.0020 |
| push | 0.33 | 1.00 | 0.0174 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.496, 0.128, 0.199) | (0.500, 0.099, 0.040)→(0.501, 0.100, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.543 | 2.127 |
| descend | descend | 1.00 / step_budget | (0.496, 0.128, 0.199)→(0.501, 0.122, 0.050) | (0.501, 0.100, 0.034)→(0.510, 0.111, 0.026) | 0.180→0.192 | 1.00 / 1.667 | 64.316 | 81.577 |
| contact | contact | 1.00 / force_exceeded | (0.501, 0.122, 0.050)→(0.501, 0.122, 0.048) | (0.510, 0.111, 0.026)→(0.511, 0.111, 0.026) | 0.192→0.192 | 1.00 / 2.000 | 1337.249 | 30.472 |
| push | push | 0.33 / guard_failure | (0.501, 0.122, 0.048)→(0.499, 0.106, 0.044) | (0.511, 0.111, 0.026)→(0.510, 0.091, 0.024) | 0.192→0.172 | 1.00 / 1.667 | 15.854 | 59.115 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.407
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.407
- phase_score: 0.510
- phase_breakdown.approach_peg_score: 0.735
- phase_breakdown.insertion_progress_score: 0.413

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.469
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.407
- **Median Q (composite search score)**: -0.198
- **K-run variance**: 0.0356
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.368


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.64623,"average_solve_count":212.0,"average_success_count":212.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.05028,"approach.approach_tolerance":0.00847,"contact.contact_force_threshold":6.09976,"contact.contact_speed":0.02381,"descend.descend_speed":0.02034,"descend.descend_tolerance":0.00441,"descend.descend_z_offset":-9e-05,"push.force_guard_threshold":35.30195,"push.push_distance":0.14034,"push.push_max_time":3.48012,"push.push_speed":0.01353},"optimized_scores":{"best_composite_score":0.19191,"best_fitness_score":0.46858,"best_task_score":0.40687},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50422,0.06892,0.0093],"force_p95":89.7455,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":105.95309,"mean_force":11.34151,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49851,0.09098,0.11609]},{"body_a":"attachment","body_b":"peg","contact_count":138.0,"contact_point_centroid":[0.51056,0.08269,0.05625],"force_p95":103.16727,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":105.39413,"mean_force":78.28613,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50164,0.08901,0.05883]},{"body_a":"peg","body_b":"channel_base_body","contact_count":986.0,"contact_point_centroid":[0.50305,0.01821,0.00826],"force_p95":23.12806,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.08516,"mean_force":2.51682,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49995,0.0623,0.0467]},{"body_a":"attachment","body_b":"peg","contact_count":126.0,"contact_point_centroid":[0.50438,0.0384,0.04328],"force_p95":31.10566,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.76425,"mean_force":15.30264,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50011,0.04913,0.04509]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50849,0.0457,0.00812],"force_p95":7.66761,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.66761,"mean_force":7.66761,"phase_index":2.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.50391,0.08957,0.05521]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50368,0.07919,0.05537],"force_p95":6.90999,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.90999,"mean_force":6.90999,"phase_index":2.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.50391,0.08957,0.05521]},{"body_a":"peg","body_b":"channel_base_body","contact_count":614.0,"contact_point_centroid":[0.50305,0.0675,0.00934],"force_p95":0.55511,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56066,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49914,0.14636,0.24365]}],"total_contact_groups":7},"final_pose_error":0.11746,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50123,0.00236,0.02402],"final_tcp_position":[0.49966,0.03913,0.04325],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":105.95309,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":630.0,"n_steps_budget":1000.0,"object_pos_end":[0.50309,0.06745,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54359,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":614.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach_peg","tcp_end":[0.50004,0.09481,0.19272],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16129,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50315,0.06285,0.03128],"object_pos_start":[0.50309,0.06745,0.0338],"object_to_goal_dist_end":0.14315,"object_to_goal_dist_start":0.14762,"object_z_max":0.03392,"peak_contact_force":90.56254,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1138.0,"raw_peak_contact_force":105.95309,"subtask_id":"approach_peg","tcp_end":[0.50391,0.08957,0.05521],"tcp_start":[0.50004,0.09481,0.19272],"tcp_to_object_dist_end":0.03588,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.06266,0.03135],"object_pos_start":[0.50315,0.06285,0.03128],"object_to_goal_dist_end":0.14296,"object_to_goal_dist_start":0.14315,"object_z_max":0.03128,"peak_contact_force":7.66761,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":7.66761,"tcp_end":[0.50389,0.08957,0.05515],"tcp_start":[0.50391,0.08957,0.05521],"tcp_to_object_dist_end":0.03593,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50123,0.00236,0.02402],"object_pos_start":[0.50305,0.06266,0.03135],"object_to_goal_dist_end":0.08391,"object_to_goal_dist_start":0.14296,"object_z_max":0.04083,"peak_contact_force":0.89059,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1112.0,"raw_peak_contact_force":32.08516,"subtask_id":"insertion_progress","tcp_end":[0.49966,0.03913,0.04325],"tcp_start":[0.50389,0.08957,0.05515],"tcp_to_object_dist_end":0.04152,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.95302,"average_solve_count":149.0,"average_success_count":149.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.06153,"approach.approach_tolerance":0.00246,"contact.contact_force_threshold":5.61055,"contact.contact_speed":0.01788,"descend.descend_speed":0.03123,"descend.descend_tolerance":0.00497,"descend.descend_z_offset":-0.00489,"push.force_guard_threshold":40.62541,"push.push_distance":0.15658,"push.push_max_time":2.93343,"push.push_speed":0.02684},"optimized_scores":{"best_composite_score":-0.21807,"best_fitness_score":0.14193,"best_task_score":0.01628},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50542,0.11327,0.0092],"force_p95":123.75153,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":135.79321,"mean_force":20.0562,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50191,0.13944,0.1193]},{"body_a":"attachment","body_b":"peg","contact_count":200.0,"contact_point_centroid":[0.51275,0.12955,0.05435],"force_p95":131.52912,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":135.16987,"mean_force":97.61067,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50404,0.13641,0.05625]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51486,0.11968,0.00791],"force_p95":83.06565,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.06565,"mean_force":83.06565,"phase_index":2.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.50721,0.13806,0.05251]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51191,0.12804,0.05283],"force_p95":82.5626,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":82.5626,"mean_force":82.5626,"phase_index":2.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.50721,0.13806,0.05251]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.49571,0.11969,0.00793],"force_p95":64.15571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":75.26441,"mean_force":19.57075,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50722,0.13806,0.05245]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.5076,0.12828,0.05442],"force_p95":63.49053,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":74.54414,"mean_force":19.05912,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50722,0.13806,0.05245]},{"body_a":"peg","body_b":"channel_base_body","contact_count":978.0,"contact_point_centroid":[0.50361,0.1117,0.00938],"force_p95":0.60828,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55297,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50152,0.17264,0.2525]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49965,0.19942,0.29953]}],"total_contact_groups":8},"final_pose_error":0.18618,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50345,0.10896,0.03262],"final_tcp_position":[0.50715,0.13805,0.05233],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":135.79321,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50371,0.11177,0.0338],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19191,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.54493,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":994.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach_peg","tcp_end":[0.50495,0.14692,0.21056],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.18022,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50364,0.10959,0.03267],"object_pos_start":[0.50371,0.11177,0.0338],"object_to_goal_dist_end":0.18977,"object_to_goal_dist_start":0.19191,"object_z_max":0.03398,"peak_contact_force":101.7835,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1200.0,"raw_peak_contact_force":135.79321,"subtask_id":"approach_peg","tcp_end":[0.50721,0.13806,0.05251],"tcp_start":[0.50495,0.14692,0.21056],"tcp_to_object_dist_end":0.03488,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50358,0.10953,0.03264],"object_pos_start":[0.50364,0.10959,0.03267],"object_to_goal_dist_end":0.1897,"object_to_goal_dist_start":0.18977,"object_z_max":0.03267,"peak_contact_force":83.06565,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":83.06565,"tcp_end":[0.50722,0.13806,0.05249],"tcp_start":[0.50721,0.13806,0.05251],"tcp_to_object_dist_end":0.03495,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.50354,0.10946,0.03262],"object_pos_start":[0.50358,0.10953,0.03264],"object_to_goal_dist_end":0.18964,"object_to_goal_dist_start":0.1897,"object_z_max":0.03264,"peak_contact_force":0.81418,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":8.0,"raw_peak_contact_force":75.26441,"subtask_id":"insertion_progress","tcp_end":[0.50715,0.13805,0.05233],"tcp_start":[0.5072,0.13806,0.0524],"tcp_to_object_dist_end":0.03491,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.86395,"average_solve_count":147.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.04962,"approach.approach_tolerance":0.00565,"contact.contact_force_threshold":8.73438,"contact.contact_speed":0.02258,"descend.descend_speed":0.03855,"descend.descend_tolerance":0.0049,"descend.descend_z_offset":0.00566,"push.force_guard_threshold":36.4807,"push.push_distance":0.18538,"push.push_max_time":4.09003,"push.push_speed":0.03387},"optimized_scores":{"best_composite_score":-0.19842,"best_fitness_score":0.16158,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.54191,0.12,0.05995],"force_p95":67.96525,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":69.99652,"mean_force":55.43229,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49152,0.13944,0.03503]},{"body_a":"peg","body_b":"world","contact_count":829.0,"contact_point_centroid":[0.50427,0.15904,-0.00188],"force_p95":0.68384,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.9851,"mean_force":0.61144,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.48737,0.14043,0.10354]},{"body_a":"peg","body_b":"channel_base_body","contact_count":552.0,"contact_point_centroid":[0.49619,0.1192,0.00941],"force_p95":0.60603,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55533,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49125,0.17059,0.24396]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49939,0.19905,0.29856]},{"body_a":"peg","body_b":"world","contact_count":54.0,"contact_point_centroid":[0.52419,0.16039,-0.00196],"force_p95":0.68373,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68373,"mean_force":0.6061,"phase_index":2.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.49124,0.13924,0.03781]},{"body_a":"peg","body_b":"world","contact_count":4.0,"contact_point_centroid":[0.52626,0.14792,-0.00196],"force_p95":0.67138,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68365,"mean_force":0.58776,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49152,0.13944,0.03503]},{"body_a":"peg","body_b":"channel_base_body","contact_count":123.0,"contact_point_centroid":[0.49617,0.11991,0.00947],"force_p95":0.57622,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59105,"mean_force":0.49778,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.48332,0.14214,0.18215]}],"total_contact_groups":7},"final_pose_error":0.16923,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.52626,0.16045,0.01412],"final_tcp_position":[0.49158,0.13943,0.03497],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":3921.01344,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":577.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.12016,0.03388],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.20029,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.53937,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":576.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach_peg","tcp_end":[0.48448,0.14288,0.19356],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16171,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":955.0,"n_steps_budget":1000.0,"object_pos_end":[0.52251,0.16039,0.01413],"object_pos_start":[0.49602,0.12016,0.03388],"object_to_goal_dist_end":0.24282,"object_to_goal_dist_start":0.20029,"object_z_max":0.03388,"peak_contact_force":0.60187,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":952.0,"raw_peak_contact_force":2.9851,"subtask_id":"approach_peg","tcp_end":[0.49148,0.1392,0.04099],"tcp_start":[0.48448,0.14288,0.19356],"tcp_to_object_dist_end":0.04619,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":54.0,"n_steps_budget":1000.0,"object_pos_end":[0.526,0.16043,0.01413],"object_pos_start":[0.52251,0.16039,0.01413],"object_to_goal_dist_end":0.24322,"object_to_goal_dist_start":0.24282,"object_z_max":0.01413,"peak_contact_force":3921.01344,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":54.0,"raw_peak_contact_force":0.68373,"tcp_end":[0.49149,0.13945,0.03508],"tcp_start":[0.49148,0.1392,0.04099],"tcp_to_object_dist_end":0.0455,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.52606,0.16039,0.01412],"object_pos_start":[0.526,0.16043,0.01413],"object_to_goal_dist_end":0.24318,"object_to_goal_dist_start":0.24322,"object_z_max":0.01413,"peak_contact_force":45.85811,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":8.0,"raw_peak_contact_force":69.99652,"subtask_id":"insertion_progress","tcp_end":[0.49158,0.13943,0.03497],"tcp_start":[0.49156,0.13944,0.03499],"tcp_to_object_dist_end":0.04542,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```