## Search State

- **Seed**: 6
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 9 | 0.1374 | 0.49 | ✅ accepted |
| 2 | approach → descend → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.2311 | 0.32 | ✅ accepted |
| 1 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0828 | 0.00 | ❌ rejected |
| 0 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0805 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.49 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.137) — your mutation base

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

- **Composite score**: 0.137
- **task_score** (E): 0.495
- **fitness_score**: 0.536  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.111
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.1662 |
| descend | 1.00 | 1.00 | 0.0912 |
| contact_seating | 1.00 | 1.00 | 0.0598 |
| push | 1.00 | 1.00 | 0.0534 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.151, 0.143) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.531 | 2.127 |
| descend | descend | 1.00 / step_budget | (0.497, 0.151, 0.143)→(0.496, 0.148, 0.052) | (0.501, 0.099, 0.034)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.533 | 0.624 |
| contact_seating | contact | 1.00 / step_budget | (0.496, 0.148, 0.052)→(0.494, 0.089, 0.044) | (0.501, 0.099, 0.034)→(0.504, 0.060, 0.040) | 0.180→0.140 | 1.00 / 2.000 | 6.638 | 7.663 |
| push | push | 1.00 / time_limit | (0.494, 0.089, 0.044)→(0.492, 0.036, 0.039) | (0.504, 0.060, 0.040)→(0.506, 0.003, 0.040) | 0.140→0.083 | 1.00 / 3.333 | 13.890 | 23.199 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.554
- alignment_error: None
- force_efficiency: 0.684
- terminal_score: 0.554
- phase_score: 0.536
- phase_breakdown.behind_peg_score: 0.915
- phase_breakdown.insertion_progress_score: 0.373

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.623
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.601
- **Median Q (composite search score)**: 0.113
- **K-run variance**: 0.0316
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.289


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.58276,"average_solve_count":290.0,"average_success_count":290.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.03517,"approach.approach_tolerance":0.00553,"contact_seating.contact_force_threshold":6.74902,"contact_seating.contact_speed":0.01825,"descend.descend_speed":0.01768,"descend.descend_tolerance":0.00579,"descend.descend_z_offset":0.0132,"push.push_max_time":2.95566,"push.push_speed":0.03214},"optimized_scores":{"best_composite_score":0.11313,"best_fitness_score":0.62313,"best_task_score":0.60111},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":173.0,"contact_point_centroid":[0.53799,0.01229,0.06],"force_p95":24.39846,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":27.03466,"mean_force":18.23717,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49278,0.01586,0.03763]},{"body_a":"attachment","body_b":"peg","contact_count":1000.0,"contact_point_centroid":[0.49874,0.02136,0.035],"force_p95":13.86645,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.97788,"mean_force":9.25157,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49237,0.03071,0.03806]},{"body_a":"peg","body_b":"channel_base_body","contact_count":995.0,"contact_point_centroid":[0.50536,-0.00311,0.00993],"force_p95":10.58074,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.68073,"mean_force":6.7965,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49237,0.03062,0.03806]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":818.0,"contact_point_centroid":[0.5251,0.00583,0.02196],"force_p95":8.1412,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.04784,"mean_force":5.7202,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49233,0.02589,0.03774]},{"body_a":"peg","body_b":"channel_base_body","contact_count":999.0,"contact_point_centroid":[0.504,0.04717,0.00979],"force_p95":5.37413,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.4639,"mean_force":2.84213,"phase_index":2.0,"phase_name":"contact_seating","phase_type":"contact","tcp_position_centroid":[0.49513,0.08621,0.04449]},{"body_a":"attachment","body_b":"peg","contact_count":686.0,"contact_point_centroid":[0.49947,0.06648,0.04339],"force_p95":5.15673,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.1287,"mean_force":3.51848,"phase_index":2.0,"phase_name":"contact_seating","phase_type":"contact","tcp_position_centroid":[0.49502,0.07754,0.04385]},{"body_a":"peg","body_b":"channel_base_body","contact_count":884.0,"contact_point_centroid":[0.50305,0.06749,0.00936],"force_p95":0.55305,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55638,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49891,0.15944,0.21836]},{"body_a":"peg","body_b":"channel_base_body","contact_count":515.0,"contact_point_centroid":[0.50311,0.06742,0.00938],"force_p95":0.55057,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55075,"mean_force":0.54665,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49791,0.11851,0.09586]}],"total_contact_groups":8},"final_pose_error":0.08534,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50732,-0.02872,0.04066],"final_tcp_position":[0.49335,0.00505,0.03757],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":27.03466,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":900.0,"n_steps_budget":1000.0,"object_pos_end":[0.50309,0.06745,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54363,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":884.0,"raw_peak_contact_force":2.06903,"subtask_id":"behind_peg","tcp_end":[0.49968,0.12073,0.14275],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12133,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":515.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50309,0.06745,0.0338],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14762,"object_z_max":0.0338,"peak_contact_force":0.54779,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":515.0,"raw_peak_contact_force":0.55075,"tcp_end":[0.49879,0.11686,0.05077],"tcp_start":[0.49968,0.12073,0.14275],"tcp_to_object_dist_end":0.05245,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50562,0.02934,0.04038],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.10948,"object_to_goal_dist_start":0.14758,"object_z_max":0.04037,"peak_contact_force":5.18304,"phase_name":"contact_seating","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1685.0,"raw_peak_contact_force":6.4639,"tcp_end":[0.49518,0.0588,0.04293],"tcp_start":[0.49879,0.11686,0.05077],"tcp_to_object_dist_end":0.03136,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50732,-0.02872,0.04066],"object_pos_start":[0.50562,0.02934,0.04038],"object_to_goal_dist_end":0.05181,"object_to_goal_dist_start":0.10948,"object_z_max":0.04069,"peak_contact_force":7.16408,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2986.0,"raw_peak_contact_force":27.03466,"subtask_id":"insertion_progress","tcp_end":[0.49335,0.00505,0.03757],"tcp_start":[0.49518,0.0588,0.04293],"tcp_to_object_dist_end":0.03667,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.89305,"average_solve_count":187.0,"average_success_count":187.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.06069,"approach.approach_tolerance":0.00447,"contact_seating.contact_force_threshold":6.98732,"contact_seating.contact_speed":0.01626,"descend.descend_speed":0.02879,"descend.descend_tolerance":0.00601,"descend.descend_z_offset":0.0158,"push.push_max_time":5.10169,"push.push_speed":0.01626},"optimized_scores":{"best_composite_score":0.36619,"best_fitness_score":0.54286,"best_task_score":0.55367},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":1000.0,"contact_point_centroid":[0.49947,0.07417,0.03846],"force_p95":14.86808,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.78781,"mean_force":10.49943,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49298,0.08344,0.04138]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50552,0.05243,0.00987],"force_p95":12.22744,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.64665,"mean_force":8.962,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49298,0.08344,0.04138]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":638.0,"contact_point_centroid":[0.5251,0.05525,0.02381],"force_p95":8.01952,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.35192,"mean_force":5.91476,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.4929,0.07376,0.04081]},{"body_a":"peg","body_b":"channel_base_body","contact_count":677.0,"contact_point_centroid":[0.50487,0.09627,0.00975],"force_p95":5.62573,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.02624,"mean_force":2.75432,"phase_index":2.0,"phase_name":"contact_seating","phase_type":"contact","tcp_position_centroid":[0.49638,0.1353,0.04815]},{"body_a":"attachment","body_b":"peg","contact_count":412.0,"contact_point_centroid":[0.50023,0.11513,0.047],"force_p95":5.47109,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.67014,"mean_force":3.79391,"phase_index":2.0,"phase_name":"contact_seating","phase_type":"contact","tcp_position_centroid":[0.49614,0.12636,0.04738]},{"body_a":"peg","body_b":"channel_base_body","contact_count":857.0,"contact_point_centroid":[0.50362,0.11167,0.00939],"force_p95":0.60978,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55282,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50229,0.18043,0.21746]},{"body_a":"peg","body_b":"channel_base_body","contact_count":425.0,"contact_point_centroid":[0.50365,0.11158,0.00941],"force_p95":0.60174,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66493,"mean_force":0.54368,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50206,0.16125,0.09784]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49968,0.19948,0.29936]}],"total_contact_groups":8},"final_pose_error":0.13701,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50726,0.02319,0.04029],"final_tcp_position":[0.4931,0.05683,0.04017],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":15.78781,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":879.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,0.11173,0.03383],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19186,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.51466,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":873.0,"raw_peak_contact_force":2.06328,"subtask_id":"behind_peg","tcp_end":[0.50631,0.16259,0.14229],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11982,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":425.0,"n_steps_budget":1000.0,"object_pos_end":[0.50374,0.11173,0.03386],"object_pos_start":[0.50372,0.11173,0.03383],"object_to_goal_dist_end":0.19186,"object_to_goal_dist_start":0.19186,"object_z_max":0.03394,"peak_contact_force":0.53063,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":425.0,"raw_peak_contact_force":0.66493,"tcp_end":[0.50011,0.16065,0.05431],"tcp_start":[0.50631,0.16259,0.14229],"tcp_to_object_dist_end":0.05315,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":677.0,"n_steps_budget":1000.0,"object_pos_end":[0.50542,0.08488,0.04024],"object_pos_start":[0.50374,0.11173,0.03386],"object_to_goal_dist_end":0.16497,"object_to_goal_dist_start":0.19186,"object_z_max":0.04024,"peak_contact_force":7.02624,"phase_name":"contact_seating","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1089.0,"raw_peak_contact_force":7.02624,"tcp_end":[0.4962,0.11266,0.04671],"tcp_start":[0.50011,0.16065,0.05431],"tcp_to_object_dist_end":0.02998,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50726,0.02319,0.04029],"object_pos_start":[0.50542,0.08488,0.04024],"object_to_goal_dist_end":0.10345,"object_to_goal_dist_start":0.16497,"object_z_max":0.0407,"peak_contact_force":13.22276,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2638.0,"raw_peak_contact_force":15.78781,"subtask_id":"insertion_progress","tcp_end":[0.4931,0.05683,0.04017],"tcp_start":[0.4962,0.11266,0.04671],"tcp_to_object_dist_end":0.0365,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.04192,"average_solve_count":167.0,"average_success_count":167.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.06376,"approach.approach_tolerance":0.0048,"contact_seating.contact_force_threshold":9.73912,"contact_seating.contact_speed":0.00934,"descend.descend_speed":0.04995,"descend.descend_tolerance":0.00388,"descend.descend_z_offset":0.00874,"push.push_max_time":5.42649,"push.push_speed":0.01561},"optimized_scores":{"best_composite_score":-0.06698,"best_fitness_score":0.44302,"best_task_score":0.32914},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":150.0,"contact_point_centroid":[0.53301,0.05374,0.06],"force_p95":22.17441,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":26.77322,"mean_force":17.04791,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48749,0.05494,0.03801]},{"body_a":"attachment","body_b":"peg","contact_count":1000.0,"contact_point_centroid":[0.49466,0.06194,0.03477],"force_p95":20.92834,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.413,"mean_force":10.12602,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48697,0.06994,0.03848]},{"body_a":"peg","body_b":"channel_base_body","contact_count":989.0,"contact_point_centroid":[0.50276,0.04114,0.00991],"force_p95":13.03578,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.74997,"mean_force":6.82237,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48698,0.06982,0.03848]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":514.0,"contact_point_centroid":[0.52523,0.04146,0.02488],"force_p95":15.04579,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.80675,"mean_force":10.97588,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48731,0.05845,0.03803]},{"body_a":"peg","body_b":"channel_base_body","contact_count":997.0,"contact_point_centroid":[0.4983,0.09389,0.00982],"force_p95":8.22098,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.49785,"mean_force":4.24182,"phase_index":2.0,"phase_name":"contact_seating","phase_type":"contact","tcp_position_centroid":[0.48808,0.13081,0.04478]},{"body_a":"attachment","body_b":"peg","contact_count":743.0,"contact_point_centroid":[0.49331,0.11133,0.04309],"force_p95":8.01675,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.16601,"mean_force":5.12324,"phase_index":2.0,"phase_name":"contact_seating","phase_type":"contact","tcp_position_centroid":[0.48826,0.12195,0.04424]},{"body_a":"peg","body_b":"channel_base_body","contact_count":730.0,"contact_point_centroid":[0.49616,0.11911,0.00943],"force_p95":0.60785,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55046,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.4909,0.18414,0.21886]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49945,0.19936,0.29852]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49609,0.1191,0.00947],"force_p95":0.6079,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65506,"mean_force":0.53839,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.48593,0.16831,0.09303]}],"total_contact_groups":9},"final_pose_error":0.12746,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50486,0.01449,0.04007],"final_tcp_position":[0.48808,0.04688,0.03802],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":26.77322,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":755.0,"n_steps_budget":1000.0,"object_pos_end":[0.496,0.11912,0.03382],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19925,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.53522,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":754.0,"raw_peak_contact_force":2.24822,"subtask_id":"behind_peg","tcp_end":[0.48381,0.16968,0.14401],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12185,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49605,0.11928,0.03394],"object_pos_start":[0.496,0.11912,0.03382],"object_to_goal_dist_end":0.19941,"object_to_goal_dist_start":0.19925,"object_z_max":0.03419,"peak_contact_force":0.52169,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.65506,"tcp_end":[0.49041,0.16792,0.05096],"tcp_start":[0.48381,0.16968,0.14401],"tcp_to_object_dist_end":0.05184,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50159,0.06583,0.04057],"object_pos_start":[0.49605,0.11928,0.03394],"object_to_goal_dist_end":0.14584,"object_to_goal_dist_start":0.19941,"object_z_max":0.0406,"peak_contact_force":7.70563,"phase_name":"contact_seating","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1740.0,"raw_peak_contact_force":9.49785,"tcp_end":[0.48934,0.09646,0.04333],"tcp_start":[0.49041,0.16792,0.05096],"tcp_to_object_dist_end":0.0331,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50486,0.01449,0.04007],"object_pos_start":[0.50159,0.06583,0.04057],"object_to_goal_dist_end":0.09462,"object_to_goal_dist_start":0.14584,"object_z_max":0.04082,"peak_contact_force":21.28274,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2653.0,"raw_peak_contact_force":26.77322,"subtask_id":"insertion_progress","tcp_end":[0.48808,0.04688,0.03802],"tcp_start":[0.48934,0.09646,0.04333],"tcp_to_object_dist_end":0.03654,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```