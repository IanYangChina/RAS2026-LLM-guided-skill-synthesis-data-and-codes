## Search State

- **Seed**: 6
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → push → lift | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5  | 0.5088 | 0.74 | ✅ accepted |
| 4 | approach → descend → push → lift | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4  | 0.3544 | 0.61 | ❌ rejected |
| 3 | approach → descend → push → lift | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4  | 0.3304 | 0.63 | ✅ accepted |
| 2 | approach → descend → push → lift | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5  | -0.0828 | 0.00 | ❌ rejected |
| 1 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5  | 0.4088 | 0.49 | ❌ rejected |

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

## Current Skill (Q=0.409) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_peg
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.02
  weight: 0.3
- id: push_progress
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
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
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
  retries:
    max_attempts: 0
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: reach_peg
- id: descend_to_peg
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
    - 0.03
    - 0.01
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
- id: push_channel
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
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
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_established
    when: before_phase
    predicate: contact_detected
    args:
      body_a: attachment
      body_b: peg
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
  subtask_id: push_progress
- id: lift_away
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: channel_exit
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_speed:
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
    offset:
    - 0.0
    - 0.0
    - 0.0

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **descend_to_peg** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, 0.01], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.005, 0.0]
- **push_channel** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_established, when=before_phase, predicate=contact_detected, on_failure=retry, threshold=1.0, args={'body_a': 'attachment', 'body_b': 'peg'}
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.005, 0.0]
- **lift_away** (`lift`)
  - target: source=yaml, anchor=task_goal, entity=channel_exit, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.409
- **task_score** (E): 0.494
- **fitness_score**: 0.469  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.2424 |
| descend_to_peg | 1.00 | 1.00 | 0.0243 |
| push_channel | 1.00 | 1.00 | 0.0490 |
| lift_away | 1.00 | 1.00 | 0.1818 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.496, 0.132, 0.069) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.552 | 2.127 |
| descend_to_peg | descend | 1.00 / step_budget | (0.496, 0.132, 0.069)→(0.497, 0.129, 0.045) | (0.501, 0.099, 0.034)→(0.501, 0.099, 0.034) | 0.180→0.179 | 1.00 / 1.000 | 0.331 | 2.975 |
| push_channel | push | 1.00 / force_exceeded | (0.497, 0.129, 0.045)→(0.495, 0.081, 0.041) | (0.501, 0.099, 0.034)→(0.507, 0.051, 0.039) | 0.179→0.132 | 1.00 / 3.000 | 56.912 | 20.676 |
| lift_away | lift | 1.00 / step_budget | (0.495, 0.081, 0.041)→(0.497, -0.067, 0.146) | (0.507, 0.051, 0.039)→(0.504, 0.019, 0.024) | 0.132→0.101 | 1.00 / 1.000 | 0.611 | 33.362 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.508
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.508
- phase_score: 0.461
- phase_breakdown.reach_peg_score: 0.822
- phase_breakdown.push_progress_score: 0.307

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.480
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.508
- **Median Q (composite search score)**: 0.409
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.260


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.05181,"average_solve_count":193.0,"average_success_count":193.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.06161,"descend_to_peg.descend_speed":0.03202,"lift_away.lift_speed":0.05556,"push_channel.push_force_threshold":33.81469,"push_channel.push_speed":0.01449},"optimized_scores":{"best_composite_score":0.40933,"best_fitness_score":0.46933,"best_task_score":0.47854},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":26.0,"contact_point_centroid":[0.50154,0.02147,0.04275],"force_p95":17.34118,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.88257,"mean_force":4.03884,"phase_index":3.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.49584,0.03156,0.0434]},{"body_a":"peg","body_b":"channel_base_body","contact_count":436.0,"contact_point_centroid":[0.5051,-0.01831,0.00826],"force_p95":0.98754,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.84281,"mean_force":0.88758,"phase_index":3.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.49533,-0.01883,0.09247]},{"body_a":"attachment","body_b":"peg","contact_count":653.0,"contact_point_centroid":[0.50089,0.05243,0.04164],"force_p95":30.25383,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.31162,"mean_force":14.69817,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49574,0.06297,0.04164]},{"body_a":"peg","body_b":"channel_base_body","contact_count":674.0,"contact_point_centroid":[0.50729,0.02846,0.00985],"force_p95":25.35075,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.67135,"mean_force":11.84088,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4958,0.06422,0.04174]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":604.0,"contact_point_centroid":[0.52522,0.03652,0.02889],"force_p95":15.0062,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.90088,"mean_force":7.94339,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4957,0.06057,0.04155]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.52522,0.01703,0.02414],"force_p95":9.16254,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.88494,"mean_force":6.0467,"phase_index":3.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.49654,0.03333,0.04214]},{"body_a":"peg","body_b":"channel_base_body","contact_count":819.0,"contact_point_centroid":[0.50302,0.06746,0.00935],"force_p95":0.55329,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55715,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49877,0.15013,0.18076]},{"body_a":"peg","body_b":"channel_base_body","contact_count":143.0,"contact_point_centroid":[0.50309,0.06733,0.00938],"force_p95":0.55058,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55077,"mean_force":0.54662,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.4981,0.0999,0.05612]}],"total_contact_groups":8},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50566,-0.02094,0.02413],"final_tcp_position":[0.49681,-0.0688,0.14396],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":43.88257,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":835.0,"n_steps_budget":1000.0,"object_pos_end":[0.50306,0.0675,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.55034,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":819.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_peg","tcp_end":[0.49936,0.10212,0.06785],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04871,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":143.0,"n_steps_budget":600.0,"object_pos_end":[0.50304,0.0675,0.0338],"object_pos_start":[0.50306,0.0675,0.0338],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14766,"object_z_max":0.0338,"peak_contact_force":0.54548,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":143.0,"raw_peak_contact_force":0.55077,"tcp_end":[0.49845,0.098,0.04561],"tcp_start":[0.49936,0.10212,0.06785],"tcp_to_object_dist_end":0.03303,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":704.0,"n_steps_budget":1000.0,"object_pos_end":[0.50757,0.00223,0.03983],"object_pos_start":[0.50304,0.0675,0.0338],"object_to_goal_dist_end":0.08257,"object_to_goal_dist_start":0.14766,"object_z_max":0.04032,"peak_contact_force":34.31162,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1931.0,"raw_peak_contact_force":34.31162,"subtask_id":"push_progress","tcp_end":[0.49666,0.03349,0.04216],"tcp_start":[0.49845,0.098,0.04561],"tcp_to_object_dist_end":0.0332,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":444.0,"n_steps_budget":1000.0,"object_pos_end":[0.50566,-0.02094,0.02413],"object_pos_start":[0.50757,0.00223,0.03983],"object_to_goal_dist_end":0.06142,"object_to_goal_dist_start":0.08257,"object_z_max":0.04017,"peak_contact_force":0.60162,"phase_name":"lift_away","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":469.0,"raw_peak_contact_force":43.88257,"tcp_end":[0.49681,-0.0688,0.14396],"tcp_start":[0.49666,0.03349,0.04216],"tcp_to_object_dist_end":0.12934,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.03687,"average_solve_count":217.0,"average_success_count":217.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.04653,"descend_to_peg.descend_speed":0.04195,"lift_away.lift_speed":0.06013,"push_channel.push_force_threshold":27.64882,"push_channel.push_speed":0.037},"optimized_scores":{"best_composite_score":0.41985,"best_fitness_score":0.47985,"best_task_score":0.50791},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":522.0,"contact_point_centroid":[0.5044,0.03277,0.0082],"force_p95":0.93577,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.92436,"mean_force":0.82282,"phase_index":3.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.49652,0.0075,0.09395]},{"body_a":"attachment","body_b":"peg","contact_count":30.0,"contact_point_centroid":[0.50273,0.07051,0.04452],"force_p95":13.56198,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.48828,"mean_force":3.87123,"phase_index":3.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.49796,0.08125,0.04508]},{"body_a":"peg","body_b":"channel_base_body","contact_count":541.0,"contact_point_centroid":[0.50437,0.07653,0.00988],"force_p95":16.1988,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.91047,"mean_force":9.27811,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49838,0.11287,0.04391]},{"body_a":"attachment","body_b":"peg","contact_count":523.0,"contact_point_centroid":[0.50148,0.10055,0.04343],"force_p95":15.80725,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.56643,"mean_force":9.18925,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49832,0.11191,0.0438]},{"body_a":"peg","body_b":"channel_base_body","contact_count":108.0,"contact_point_centroid":[0.5036,0.11066,0.00941],"force_p95":0.61456,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.51727,"mean_force":0.60181,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50305,0.14271,0.05833]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52501,0.03523,0.05774],"force_p95":5.06282,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.32929,"mean_force":2.66464,"phase_index":3.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.49891,0.08437,0.04387]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.50313,0.12972,0.0588],"force_p95":4.24142,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.03049,"mean_force":1.40435,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50128,0.14175,0.04904]},{"body_a":"peg","body_b":"channel_base_body","contact_count":773.0,"contact_point_centroid":[0.50358,0.11165,0.00939],"force_p95":0.60772,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55398,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50212,0.17117,0.18063]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49975,0.19944,0.2991]}],"total_contact_groups":9},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50517,0.03051,0.02413],"final_tcp_position":[0.49707,-0.06635,0.14582],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":60.27254,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":795.0,"n_steps_budget":1000.0,"object_pos_end":[0.50378,0.11181,0.03382],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19194,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.56529,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":789.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_peg","tcp_end":[0.50591,0.14409,0.06863],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04751,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":108.0,"n_steps_budget":600.0,"object_pos_end":[0.50375,0.11163,0.03381],"object_pos_start":[0.50378,0.11181,0.03382],"object_to_goal_dist_end":0.19177,"object_to_goal_dist_start":0.19194,"object_z_max":0.03393,"peak_contact_force":0.02525,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":113.0,"raw_peak_contact_force":5.51727,"tcp_end":[0.50115,0.14166,0.04805],"tcp_start":[0.50591,0.14409,0.06863],"tcp_to_object_dist_end":0.03334,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":542.0,"n_steps_budget":1000.0,"object_pos_end":[0.50695,0.05278,0.03995],"object_pos_start":[0.50375,0.11163,0.03381],"object_to_goal_dist_end":0.13296,"object_to_goal_dist_start":0.19177,"object_z_max":0.04049,"peak_contact_force":60.27254,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1064.0,"raw_peak_contact_force":19.91047,"subtask_id":"push_progress","tcp_end":[0.49891,0.08442,0.04388],"tcp_start":[0.50115,0.14166,0.04805],"tcp_to_object_dist_end":0.03288,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":529.0,"n_steps_budget":1000.0,"object_pos_end":[0.50517,0.03051,0.02413],"object_pos_start":[0.50695,0.05278,0.03995],"object_to_goal_dist_end":0.11177,"object_to_goal_dist_start":0.13296,"object_z_max":0.03995,"peak_contact_force":0.60163,"phase_name":"lift_away","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":554.0,"raw_peak_contact_force":36.92436,"tcp_end":[0.49707,-0.06635,0.14582],"tcp_start":[0.49891,0.08442,0.04388],"tcp_to_object_dist_end":0.15575,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.13107,"average_solve_count":206.0,"average_success_count":206.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.06752,"descend_to_peg.descend_speed":0.04904,"lift_away.lift_speed":0.04726,"push_channel.push_force_threshold":27.53281,"push_channel.push_speed":0.04798},"optimized_scores":{"best_composite_score":0.39734,"best_fitness_score":0.45734,"best_task_score":0.49514},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":143.0,"contact_point_centroid":[0.49641,0.08507,0.05192],"force_p95":17.19403,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.27944,"mean_force":8.42141,"phase_index":3.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.48755,0.09311,0.05181]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":244.0,"contact_point_centroid":[0.52534,0.06924,0.03907],"force_p95":16.69394,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.48025,"mean_force":6.59986,"phase_index":3.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.4879,0.08198,0.05812]},{"body_a":"peg","body_b":"channel_base_body","contact_count":471.0,"contact_point_centroid":[0.50214,0.05502,0.00853],"force_p95":7.55126,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.8637,"mean_force":1.40317,"phase_index":3.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.49202,0.01112,0.10065]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":63.0,"contact_point_centroid":[0.47466,0.07154,0.03145],"force_p95":11.54713,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.62126,"mean_force":6.09631,"phase_index":3.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.48903,0.05281,0.07511]},{"body_a":"peg","body_b":"channel_base_body","contact_count":175.0,"contact_point_centroid":[0.50336,0.09266,0.00994],"force_p95":6.53699,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.80587,"mean_force":3.42459,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48894,0.13605,0.03785]},{"body_a":"attachment","body_b":"peg","contact_count":148.0,"contact_point_centroid":[0.49463,0.12469,0.04767],"force_p95":6.21587,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.25315,"mean_force":3.52605,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48886,0.13582,0.03774]},{"body_a":"peg","body_b":"channel_base_body","contact_count":400.0,"contact_point_centroid":[0.49691,0.11413,0.00957],"force_p95":1.76823,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.85757,"mean_force":0.69876,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48683,0.14894,0.05171]},{"body_a":"attachment","body_b":"peg","contact_count":73.0,"contact_point_centroid":[0.49371,0.13643,0.05967],"force_p95":2.10612,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.49609,"mean_force":1.09807,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.4898,0.14834,0.04422]},{"body_a":"peg","body_b":"channel_base_body","contact_count":725.0,"contact_point_centroid":[0.49617,0.11908,0.00945],"force_p95":0.61038,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.54863,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49078,0.17448,0.18027]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49955,0.19921,0.29774]}],"total_contact_groups":10},"final_pose_error":0.01983,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50074,0.04813,0.02424],"final_tcp_position":[0.49638,-0.06566,0.14679],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":76.15285,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":750.0,"n_steps_budget":1000.0,"object_pos_end":[0.49604,0.11904,0.03399],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19917,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.54124,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":749.0,"raw_peak_contact_force":2.24822,"subtask_id":"reach_peg","tcp_end":[0.48354,0.1509,0.06926],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04914,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":400.0,"n_steps_budget":600.0,"object_pos_end":[0.49612,0.11828,0.03498],"object_pos_start":[0.49604,0.11904,0.03399],"object_to_goal_dist_end":0.19838,"object_to_goal_dist_start":0.19917,"object_z_max":0.03498,"peak_contact_force":0.4221,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":473.0,"raw_peak_contact_force":2.85757,"tcp_end":[0.49119,0.14816,0.04133],"tcp_start":[0.48354,0.1509,0.06926],"tcp_to_object_dist_end":0.03094,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":220.0,"n_steps_budget":1000.0,"object_pos_end":[0.50635,0.09933,0.03645],"object_pos_start":[0.49612,0.11828,0.03498],"object_to_goal_dist_end":0.17948,"object_to_goal_dist_start":0.19838,"object_z_max":0.03646,"peak_contact_force":76.15285,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":323.0,"raw_peak_contact_force":7.80587,"subtask_id":"push_progress","tcp_end":[0.48878,0.12375,0.03693],"tcp_start":[0.49119,0.14816,0.04133],"tcp_to_object_dist_end":0.03008,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":645.0,"n_steps_budget":1000.0,"object_pos_end":[0.50074,0.04813,0.02424],"object_pos_start":[0.50635,0.09933,0.03645],"object_to_goal_dist_end":0.1291,"object_to_goal_dist_start":0.17948,"object_z_max":0.04332,"peak_contact_force":0.63077,"phase_name":"lift_away","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":921.0,"raw_peak_contact_force":19.27944,"tcp_end":[0.49638,-0.06566,0.14679],"tcp_start":[0.48878,0.12375,0.03693],"tcp_to_object_dist_end":0.16729,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```