## Search State

- **Seed**: 6
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → align → push → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7  | 0.1555 | 0.73 | ❌ rejected |
| 13 | approach → descend → push → lift | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | 8  | 0.3551 | 0.74 | ❌ rejected |
| 12 | approach → descend → push → lift | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | time_limit | time_limit | pose_tolerance | pose_tolerance | 5  | 0.4744 | 0.91 | ❌ rejected |
| 11 | approach → descend → push → lift | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7  | 0.5263 | 0.86 | ❌ rejected |
| 10 | approach → descend → push → lift | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5  | 0.3516 | 0.87 | ❌ rejected |

**Proposal policy**: task_score is 0.87 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.914, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.352) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_peg
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.0
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
    - 0.0
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
    - 0.0
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
      mode: keep_current
  parameters:
    force_limit:
      type: scalar
      range:
      - 10.0
      - 40.0
      default: 30.0
      binds_to:
      - path: guards.force_guard.threshold
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
    args:
      group: contact
    threshold: 30.0
    on_failure: retry
  retries:
    max_attempts: 3
    strategy: offset_target
    offset:
    - 0.002
    - -0.002
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
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **descend_to_peg** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.005, 0.0]
- **push_channel** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - force_limit: status=consumed; consumers=guards.force_guard.threshold (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=30.0, args={'group': 'contact'}
  - retries: max_attempts=3, strategy=offset_target, offset=[0.002, -0.002, 0.0]
- **lift_away** (`lift`)
  - target: source=yaml, anchor=task_goal, entity=channel_exit, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.352
- **task_score** (E): 0.874
- **fitness_score**: 0.792  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_high | 1.00 | 1.00 | 0.1673 |
| descend_behind | 1.00 | 1.00 | 0.1116 |
| align_behind_goal | 1.00 | 1.00 | 0.0415 |
| push_channel | 1.00 | 1.00 | 0.0865 |
| lift_away | 1.00 | 1.00 | 0.1148 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_high | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.134, 0.148) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.544 | 2.127 |
| descend_behind | descend | 1.00 / step_budget | (0.497, 0.134, 0.148)→(0.497, 0.129, 0.037) | (0.501, 0.099, 0.034)→(0.501, 0.099, 0.035) | 0.180→0.179 | 1.00 / 1.667 | 1.751 | 5.550 |
| align_behind_goal | align | 1.00 / step_budget | (0.497, 0.129, 0.037)→(0.496, 0.088, 0.035) | (0.501, 0.099, 0.035)→(0.507, 0.060, 0.036) | 0.179→0.140 | 1.00 / 2.000 | 2.927 | 11.199 |
| push_channel | push | 1.00 / time_limit | (0.496, 0.088, 0.035)→(0.494, 0.001, 0.033) | (0.507, 0.060, 0.036)→(0.507, -0.026, 0.036) | 0.140→0.054 | 1.00 / 3.000 | 4.021 | 13.210 |
| lift_away | lift | 1.00 / step_budget | (0.494, 0.001, 0.033)→(0.496, -0.070, 0.123) | (0.507, -0.026, 0.036)→(0.500, -0.062, 0.033) | 0.054→0.020 | 1.00 / 1.000 | 0.437 | 13.189 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.625
- terminal_score: 1.000
- phase_score: 0.721
- phase_breakdown.reach_peg_score: 0.811
- phase_breakdown.push_progress_score: 0.627
- phase_breakdown.pre_push_score: 0.820

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.833
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.362
- **K-run variance**: 0.0015
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.306


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45882,"average_solve_count":170.0,"average_success_count":170.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind_goal.align_speed":0.06067,"approach_high.approach_speed":0.07068,"descend_behind.descend_speed":0.07554,"lift_away.lift_speed":0.1038,"push_channel.force_limit":31.82038,"push_channel.push_duration":6.46025,"push_channel.push_speed":0.05656},"optimized_scores":{"best_composite_score":0.362,"best_fitness_score":0.802,"best_task_score":0.83479},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_left_wall","contact_count":82.0,"contact_point_centroid":[0.52508,-0.04385,0.04393],"force_p95":12.53568,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.6292,"mean_force":2.5582,"phase_index":4.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.49334,-0.01815,0.04886]},{"body_a":"attachment","body_b":"peg","contact_count":56.0,"contact_point_centroid":[0.4992,-0.02789,0.04848],"force_p95":12.92464,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.60107,"mean_force":3.96903,"phase_index":4.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.49338,-0.01739,0.04793]},{"body_a":"attachment","body_b":"peg","contact_count":877.0,"contact_point_centroid":[0.49993,0.029,0.03879],"force_p95":7.00921,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.62563,"mean_force":2.6822,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49399,0.03998,0.0322]},{"body_a":"peg","body_b":"channel_base_body","contact_count":296.0,"contact_point_centroid":[0.50385,-0.05052,0.00996],"force_p95":1.34361,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.02371,"mean_force":0.64948,"phase_index":4.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.49425,-0.04003,0.07913]},{"body_a":"peg","body_b":"channel_base_body","contact_count":46.0,"contact_point_centroid":[0.50178,0.04842,0.00982],"force_p95":9.23508,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.94582,"mean_force":2.87928,"phase_index":2.0,"phase_name":"align_behind_goal","phase_type":"align","tcp_position_centroid":[0.49758,0.09358,0.03533]},{"body_a":"attachment","body_b":"peg","contact_count":41.0,"contact_point_centroid":[0.50068,0.08122,0.04381],"force_p95":8.98128,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.68766,"mean_force":2.7854,"phase_index":2.0,"phase_name":"align_behind_goal","phase_type":"align","tcp_position_centroid":[0.49738,0.09298,0.03519]},{"body_a":"peg","body_b":"channel_base_body","contact_count":654.0,"contact_point_centroid":[0.50673,-0.00238,0.00996],"force_p95":6.45063,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.94101,"mean_force":3.46277,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49405,0.04104,0.03225]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":689.0,"contact_point_centroid":[0.52506,0.01216,0.02455],"force_p95":3.35841,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.68833,"mean_force":1.36723,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49405,0.0386,0.03228]},{"body_a":"peg","body_b":"channel_base_body","contact_count":580.0,"contact_point_centroid":[0.5033,0.0666,0.00939],"force_p95":0.5507,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.32471,"mean_force":0.57331,"phase_index":1.0,"phase_name":"descend_behind","phase_type":"descend","tcp_position_centroid":[0.49812,0.10036,0.08997]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.50233,0.08532,0.05905],"force_p95":4.27772,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.85964,"mean_force":1.88792,"phase_index":1.0,"phase_name":"descend_behind","phase_type":"descend","tcp_position_centroid":[0.49897,0.09738,0.03977]},{"body_a":"peg","body_b":"channel_base_body","contact_count":577.0,"contact_point_centroid":[0.50302,0.06749,0.00934],"force_p95":0.55531,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56156,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49903,0.15115,0.22045]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":5.0,"contact_point_centroid":[0.47493,-0.08024,0.0486],"force_p95":0.93978,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.97276,"mean_force":0.69527,"phase_index":4.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.49607,-0.06826,0.11893]}],"total_contact_groups":12},"final_pose_error":0.01975,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49845,-0.06611,0.03605],"final_tcp_position":[0.49632,-0.07098,0.12282],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":14.6292,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":593.0,"n_steps_budget":1000.0,"object_pos_end":[0.50309,0.06748,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.5473,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":577.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_peg","tcp_end":[0.4998,0.10408,0.14647],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11851,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":580.0,"n_steps_budget":930.0,"object_pos_end":[0.50285,0.06716,0.03449],"object_pos_start":[0.50309,0.06748,0.0338],"object_to_goal_dist_end":0.14729,"object_to_goal_dist_start":0.14764,"object_z_max":0.03445,"peak_contact_force":0.47645,"phase_name":"descend_behind","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":590.0,"raw_peak_contact_force":5.32471,"subtask_id":"reach_peg","tcp_end":[0.49899,0.09719,0.03652],"tcp_start":[0.4998,0.10408,0.14647],"tcp_to_object_dist_end":0.03035,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":62.0,"n_steps_budget":600.0,"object_pos_end":[0.50522,0.05923,0.03636],"object_pos_start":[0.50285,0.06716,0.03449],"object_to_goal_dist_end":0.13937,"object_to_goal_dist_start":0.14729,"object_z_max":0.03636,"peak_contact_force":0.22513,"phase_name":"align_behind_goal","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":87.0,"raw_peak_contact_force":9.94582,"subtask_id":"pre_push","tcp_end":[0.49667,0.08791,0.03492],"tcp_start":[0.49899,0.09719,0.03652],"tcp_to_object_dist_end":0.02997,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50708,-0.03327,0.03627],"object_pos_start":[0.50522,0.05923,0.03636],"object_to_goal_dist_end":0.04741,"object_to_goal_dist_start":0.13937,"object_z_max":0.03655,"peak_contact_force":1.29999,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2220.0,"raw_peak_contact_force":11.62563,"subtask_id":"push_progress","tcp_end":[0.49489,-0.0056,0.03362],"tcp_start":[0.49667,0.08791,0.03492],"tcp_to_object_dist_end":0.03036,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":326.0,"n_steps_budget":810.0,"object_pos_end":[0.49845,-0.06611,0.03605],"object_pos_start":[0.50708,-0.03327,0.03627],"object_to_goal_dist_end":0.01453,"object_to_goal_dist_start":0.04741,"object_z_max":0.04078,"peak_contact_force":0.39289,"phase_name":"lift_away","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":439.0,"raw_peak_contact_force":14.6292,"subtask_id":"push_progress","tcp_end":[0.49632,-0.07098,0.12282],"tcp_start":[0.49489,-0.0056,0.03362],"tcp_to_object_dist_end":0.08694,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41139,"average_solve_count":158.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind_goal.align_speed":0.05154,"approach_high.approach_speed":0.09821,"descend_behind.descend_speed":0.06541,"lift_away.lift_speed":0.12443,"push_channel.force_limit":26.1657,"push_channel.push_duration":3.74351,"push_channel.push_speed":0.04544},"optimized_scores":{"best_composite_score":0.39266,"best_fitness_score":0.83266,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":910.0,"contact_point_centroid":[0.49954,0.03774,0.03766],"force_p95":6.05597,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.73738,"mean_force":2.62427,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49345,0.04858,0.03197]},{"body_a":"peg","body_b":"channel_base_body","contact_count":712.0,"contact_point_centroid":[0.5068,0.00622,0.00997],"force_p95":5.42152,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.78926,"mean_force":3.15863,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49346,0.04926,0.03197]},{"body_a":"attachment","body_b":"peg","contact_count":45.0,"contact_point_centroid":[0.49895,-0.00836,0.04233],"force_p95":9.41563,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.84796,"mean_force":1.98719,"phase_index":4.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.49292,0.00204,0.04209]},{"body_a":"attachment","body_b":"peg","contact_count":209.0,"contact_point_centroid":[0.5009,0.10104,0.04396],"force_p95":8.7848,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.47958,"mean_force":2.68654,"phase_index":2.0,"phase_name":"align_behind_goal","phase_type":"align","tcp_position_centroid":[0.49668,0.1126,0.03431]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":61.0,"contact_point_centroid":[0.52511,-0.02668,0.03642],"force_p95":7.7118,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.99185,"mean_force":1.10464,"phase_index":4.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.49294,-0.00124,0.04562]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":98.0,"contact_point_centroid":[0.52514,0.07128,0.03602],"force_p95":8.59143,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.2997,"mean_force":2.12431,"phase_index":2.0,"phase_name":"align_behind_goal","phase_type":"align","tcp_position_centroid":[0.49613,0.09926,0.03434]},{"body_a":"peg","body_b":"channel_base_body","contact_count":174.0,"contact_point_centroid":[0.50456,0.07304,0.00984],"force_p95":8.00094,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.25435,"mean_force":2.92214,"phase_index":2.0,"phase_name":"align_behind_goal","phase_type":"align","tcp_position_centroid":[0.49686,0.11566,0.03438]},{"body_a":"peg","body_b":"channel_base_body","contact_count":317.0,"contact_point_centroid":[0.50666,-0.03762,0.00992],"force_p95":1.90092,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.94721,"mean_force":0.69055,"phase_index":4.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.49392,-0.03082,0.07863]},{"body_a":"peg","body_b":"channel_base_body","contact_count":575.0,"contact_point_centroid":[0.50376,0.10936,0.00943],"force_p95":0.70233,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.52557,"mean_force":0.61452,"phase_index":1.0,"phase_name":"descend_behind","phase_type":"descend","tcp_position_centroid":[0.5019,0.143,0.0912]},{"body_a":"attachment","body_b":"peg","contact_count":32.0,"contact_point_centroid":[0.50264,0.12943,0.05843],"force_p95":4.2179,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.18167,"mean_force":1.57979,"phase_index":1.0,"phase_name":"descend_behind","phase_type":"descend","tcp_position_centroid":[0.50038,0.14142,0.04819]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":759.0,"contact_point_centroid":[0.52504,0.0231,0.02372],"force_p95":2.70599,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.17421,"mean_force":1.32766,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49344,0.04917,0.03196]},{"body_a":"peg","body_b":"channel_base_body","contact_count":475.0,"contact_point_centroid":[0.50358,0.11159,0.00938],"force_p95":0.61723,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55989,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.50241,0.17192,0.22066]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49983,0.19927,0.29882]}],"total_contact_groups":13},"final_pose_error":0.01972,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5053,-0.06213,0.02475],"final_tcp_position":[0.49636,-0.06969,0.12358],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":18.73738,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":497.0,"n_steps_budget":1000.0,"object_pos_end":[0.50369,0.11177,0.03383],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.57192,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":491.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_peg","tcp_end":[0.50626,0.14571,0.1481],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11923,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":575.0,"n_steps_budget":1000.0,"object_pos_end":[0.50393,0.1113,0.03468],"object_pos_start":[0.50369,0.11177,0.03383],"object_to_goal_dist_end":0.19141,"object_to_goal_dist_start":0.1919,"object_z_max":0.03472,"peak_contact_force":1.32492,"phase_name":"descend_behind","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":607.0,"raw_peak_contact_force":6.52557,"subtask_id":"reach_peg","tcp_end":[0.50002,0.14104,0.03703],"tcp_start":[0.50626,0.14571,0.1481],"tcp_to_object_dist_end":0.03009,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":296.0,"n_steps_budget":750.0,"object_pos_end":[0.50709,0.05974,0.03591],"object_pos_start":[0.50393,0.1113,0.03468],"object_to_goal_dist_end":0.13998,"object_to_goal_dist_start":0.19141,"object_z_max":0.03654,"peak_contact_force":7.79962,"phase_name":"align_behind_goal","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":481.0,"raw_peak_contact_force":10.47958,"subtask_id":"pre_push","tcp_end":[0.49614,0.08758,0.03494],"tcp_start":[0.50002,0.14104,0.03703],"tcp_to_object_dist_end":0.02994,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50706,-0.0159,0.03633],"object_pos_start":[0.50709,0.05974,0.03591],"object_to_goal_dist_end":0.06459,"object_to_goal_dist_start":0.13998,"object_z_max":0.03653,"peak_contact_force":4.22785,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2381.0,"raw_peak_contact_force":18.73738,"subtask_id":"push_progress","tcp_end":[0.49425,0.01152,0.03306],"tcp_start":[0.49614,0.08758,0.03494],"tcp_to_object_dist_end":0.03043,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":344.0,"n_steps_budget":720.0,"object_pos_end":[0.5053,-0.06213,0.02475],"object_pos_start":[0.50706,-0.0159,0.03633],"object_to_goal_dist_end":0.02408,"object_to_goal_dist_start":0.06459,"object_z_max":0.04078,"peak_contact_force":0.4415,"phase_name":"lift_away","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":423.0,"raw_peak_contact_force":10.84796,"subtask_id":"push_progress","tcp_end":[0.49636,-0.06969,0.12358],"tcp_start":[0.49425,0.01152,0.03306],"tcp_to_object_dist_end":0.09953,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.23958,"average_solve_count":192.0,"average_success_count":192.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind_goal.align_speed":0.04409,"approach_high.approach_speed":0.06192,"descend_behind.descend_speed":0.06102,"lift_away.lift_speed":0.10378,"push_channel.force_limit":30.36231,"push_channel.push_duration":5.69379,"push_channel.push_speed":0.05424},"optimized_scores":{"best_composite_score":0.30027,"best_fitness_score":0.74027,"best_task_score":0.78624},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":65.0,"contact_point_centroid":[0.49893,-0.02714,0.04968],"force_p95":13.38408,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.08858,"mean_force":3.16394,"phase_index":4.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.4929,-0.01682,0.05018]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":113.0,"contact_point_centroid":[0.52513,-0.04047,0.03595],"force_p95":10.80033,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.83948,"mean_force":1.8643,"phase_index":4.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.49276,-0.0176,0.05103]},{"body_a":"attachment","body_b":"peg","contact_count":272.0,"contact_point_centroid":[0.49796,0.10474,0.04133],"force_p95":10.72092,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.17146,"mean_force":4.59542,"phase_index":2.0,"phase_name":"align_behind_goal","phase_type":"align","tcp_position_centroid":[0.49209,0.11564,0.03375]},{"body_a":"peg","body_b":"channel_base_body","contact_count":280.0,"contact_point_centroid":[0.50118,-0.04738,0.00992],"force_p95":1.32347,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.70025,"mean_force":0.69922,"phase_index":4.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.49398,-0.03937,0.08024]},{"body_a":"peg","body_b":"channel_base_body","contact_count":219.0,"contact_point_centroid":[0.50441,0.07483,0.00993],"force_p95":9.78713,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.29075,"mean_force":4.96725,"phase_index":2.0,"phase_name":"align_behind_goal","phase_type":"align","tcp_position_centroid":[0.49189,0.11829,0.03374]},{"body_a":"attachment","body_b":"peg","contact_count":881.0,"contact_point_centroid":[0.49924,0.03052,0.03781],"force_p95":6.85797,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.26622,"mean_force":2.56018,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49297,0.04127,0.0322]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":228.0,"contact_point_centroid":[0.5252,0.07881,0.03191],"force_p95":7.47711,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.7291,"mean_force":2.4366,"phase_index":2.0,"phase_name":"align_behind_goal","phase_type":"align","tcp_position_centroid":[0.49297,0.10501,0.03387]},{"body_a":"peg","body_b":"channel_base_body","contact_count":663.0,"contact_point_centroid":[0.50673,-0.00066,0.00997],"force_p95":6.02021,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.89416,"mean_force":3.25488,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49301,0.04208,0.03224]},{"body_a":"peg","body_b":"channel_base_body","contact_count":686.0,"contact_point_centroid":[0.49622,0.11682,0.00946],"force_p95":0.63129,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.80053,"mean_force":0.60574,"phase_index":1.0,"phase_name":"descend_behind","phase_type":"descend","tcp_position_centroid":[0.48675,0.14989,0.09013]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":702.0,"contact_point_centroid":[0.52504,0.01443,0.02383],"force_p95":3.11971,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.40587,"mean_force":1.31317,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49309,0.04029,0.03232]},{"body_a":"attachment","body_b":"peg","contact_count":32.0,"contact_point_centroid":[0.49427,0.13645,0.0591],"force_p95":3.39359,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.39373,"mean_force":1.71334,"phase_index":1.0,"phase_name":"descend_behind","phase_type":"descend","tcp_position_centroid":[0.49081,0.14841,0.04392]},{"body_a":"peg","body_b":"channel_base_body","contact_count":483.0,"contact_point_centroid":[0.49625,0.11905,0.00939],"force_p95":0.61563,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55844,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49129,0.17531,0.22095]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49947,0.19907,0.29791]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":25.0,"contact_point_centroid":[0.47484,-0.06369,0.05858],"force_p95":0.27048,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30191,"mean_force":0.08142,"phase_index":4.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.49493,-0.05546,0.10189]}],"total_contact_groups":14},"final_pose_error":0.01989,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49597,-0.05854,0.03812],"final_tcp_position":[0.49625,-0.07067,0.12284],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":14.08858,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":508.0,"n_steps_budget":1000.0,"object_pos_end":[0.49603,0.11904,0.03401],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19917,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.51389,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":507.0,"raw_peak_contact_force":2.24822,"subtask_id":"reach_peg","tcp_end":[0.48446,0.15245,0.14896],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12027,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":686.0,"n_steps_budget":1000.0,"object_pos_end":[0.49593,0.11843,0.03475],"object_pos_start":[0.49603,0.11904,0.03401],"object_to_goal_dist_end":0.19854,"object_to_goal_dist_start":0.19917,"object_z_max":0.03479,"peak_contact_force":3.45022,"phase_name":"descend_behind","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":718.0,"raw_peak_contact_force":4.80053,"subtask_id":"reach_peg","tcp_end":[0.49152,0.14817,0.03597],"tcp_start":[0.48446,0.15245,0.14896],"tcp_to_object_dist_end":0.03009,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":370.0,"n_steps_budget":990.0,"object_pos_end":[0.50722,0.05963,0.03629],"object_pos_start":[0.49593,0.11843,0.03475],"object_to_goal_dist_end":0.13987,"object_to_goal_dist_start":0.19854,"object_z_max":0.03683,"peak_contact_force":0.75505,"phase_name":"align_behind_goal","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":719.0,"raw_peak_contact_force":13.17146,"subtask_id":"pre_push","tcp_end":[0.49521,0.08708,0.03495],"tcp_start":[0.49152,0.14817,0.03597],"tcp_to_object_dist_end":0.02999,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50693,-0.03001,0.03607],"object_pos_start":[0.50722,0.05963,0.03629],"object_to_goal_dist_end":0.05063,"object_to_goal_dist_start":0.13987,"object_z_max":0.03665,"peak_contact_force":6.53489,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2246.0,"raw_peak_contact_force":9.26622,"subtask_id":"push_progress","tcp_end":[0.49425,-0.00275,0.03353],"tcp_start":[0.49521,0.08708,0.03495],"tcp_to_object_dist_end":0.03017,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":330.0,"n_steps_budget":810.0,"object_pos_end":[0.49597,-0.05854,0.03812],"object_pos_start":[0.50693,-0.03001,0.03607],"object_to_goal_dist_end":0.02192,"object_to_goal_dist_start":0.05063,"object_z_max":0.04193,"peak_contact_force":0.47574,"phase_name":"lift_away","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":483.0,"raw_peak_contact_force":14.08858,"subtask_id":"push_progress","tcp_end":[0.49625,-0.07067,0.12284],"tcp_start":[0.49425,-0.00275,0.03353],"tcp_to_object_dist_end":0.08559,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```