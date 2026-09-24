## Search State

- **Seed**: 6
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → push → lift | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4  | 0.3544 | 0.61 | ❌ rejected |
| 3 | approach → descend → push → lift | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4  | 0.3304 | 0.63 | ✅ accepted |
| 2 | approach → descend → push → lift | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5  | -0.0828 | 0.00 | ❌ rejected |
| 1 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5  | -0.0805 | 0.00 | ✅ accepted |
| 0 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5  | 0.5088 | 0.74 | ✅ accepted |

**Proposal policy**: task_score is 0.74 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.735, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.509) — your mutation base

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

- **Composite score**: 0.509
- **task_score** (E): 0.735
- **fitness_score**: 0.769  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.2422 |
| descend_to_peg | 1.00 | 1.00 | 0.0245 |
| push_channel | 0.00 | 1.00 | 0.0297 |
| lift_away | 0.00 | 1.00 | 0.0200 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.496, 0.132, 0.069) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.510 | 2.127 |
| descend_to_peg | descend | 1.00 / step_budget | (0.496, 0.132, 0.069)→(0.497, 0.129, 0.045) | (0.501, 0.099, 0.034)→(0.501, 0.099, 0.034) | 0.180→0.179 | 1.00 / 1.333 | 0.656 | 2.081 |
| push_channel | push | 0.00 / step_budget | (0.497, 0.129, 0.045)→(0.516, 0.110, 0.045) | (0.501, 0.099, 0.034)→(0.500, -0.045, 0.024) | 0.179→0.039 | 1.00 / 3.000 | 336.786 | 1146.994 |
| lift_away | lift | 0.00 / step_budget | (0.516, 0.110, 0.045)→(0.517, 0.105, 0.050) | (0.500, -0.045, 0.024)→(0.500, -0.046, 0.024) | 0.039→0.037 | 1.00 / 2.667 | 271.737 | 525.470 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.948
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.839
- phase_score: 0.788
- phase_breakdown.reach_peg_score: 0.819
- phase_breakdown.push_progress_score: 0.775

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.808
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.839
- **Median Q (composite search score)**: 0.497
- **K-run variance**: 0.0008
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.279


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.2602,"average_solve_count":196.0,"average_success_count":196.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.05875,"descend_to_peg.descend_speed":0.05028,"lift_away.lift_speed":0.07191,"push_channel.push_speed":0.06351},"optimized_scores":{"best_composite_score":0.48113,"best_fitness_score":0.74113,"best_task_score":0.72084},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":698.0,"contact_point_centroid":[0.52515,0.08239,0.05038],"force_p95":413.40395,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1248.36712,"mean_force":375.83391,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51324,0.08099,0.04967]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":990.0,"contact_point_centroid":[0.47417,0.11991,0.05995],"force_p95":567.6273,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1049.65687,"mean_force":425.8203,"phase_index":3.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.51342,0.08939,0.04721]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":213.0,"contact_point_centroid":[0.53084,0.11967,0.05995],"force_p95":496.92199,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":702.69541,"mean_force":268.16945,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5102,0.07847,0.05667]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":940.0,"contact_point_centroid":[0.52504,0.09175,0.04823],"force_p95":411.93361,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":657.11105,"mean_force":290.45838,"phase_index":3.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.51342,0.08932,0.04717]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":792.0,"contact_point_centroid":[0.47494,0.11989,0.05527],"force_p95":594.5702,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":621.96444,"mean_force":477.76361,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51303,0.08077,0.05022]},{"body_a":"world","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.50406,0.14412,-2e-05],"force_p95":348.07158,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":356.65147,"mean_force":244.32531,"phase_index":3.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.51337,0.08286,0.04928]},{"body_a":"world","body_b":"link7","contact_count":711.0,"contact_point_centroid":[0.50671,0.14163,-4e-05],"force_p95":183.06115,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":211.01618,"mean_force":152.28637,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51326,0.08094,0.05]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50178,0.08453,0.04946],"force_p95":92.65969,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":96.10289,"mean_force":55.01049,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50006,0.09636,0.04447]},{"body_a":"peg","body_b":"channel_base_body","contact_count":955.0,"contact_point_centroid":[0.49822,-0.0401,0.00816],"force_p95":0.74928,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":94.41925,"mean_force":0.80631,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51242,0.08043,0.05159]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49828,-0.04335,0.00805],"force_p95":0.7375,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.91657,"mean_force":0.71933,"phase_index":3.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.51342,0.08944,0.04723]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.475,-0.06577,0.02416],"force_p95":5.60087,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.73793,"mean_force":3.78575,"phase_index":3.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.51371,0.09331,0.04873]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":14.0,"contact_point_centroid":[0.47496,-0.0636,0.02432],"force_p95":5.68683,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.70026,"mean_force":2.23558,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51241,0.07956,0.05617]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":31.0,"contact_point_centroid":[0.52539,0.01955,0.04136],"force_p95":1.92585,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.67936,"mean_force":0.71605,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51018,0.08053,0.04705]},{"body_a":"peg","body_b":"channel_base_body","contact_count":832.0,"contact_point_centroid":[0.50309,0.06747,0.00935],"force_p95":0.5532,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55699,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49876,0.15013,0.18076]},{"body_a":"peg","body_b":"channel_base_body","contact_count":144.0,"contact_point_centroid":[0.50306,0.06745,0.00938],"force_p95":0.55058,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55077,"mean_force":0.54665,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.4981,0.0999,0.05615]}],"total_contact_groups":15},"final_pose_error":0.20016,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49834,-0.04787,0.02418],"final_tcp_position":[0.51423,0.09832,0.05022],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":1248.36712,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":848.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54783,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":832.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_peg","tcp_end":[0.49937,0.10218,0.06798],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04889,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":144.0,"n_steps_budget":600.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14758,"object_z_max":0.0338,"peak_contact_force":0.54775,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":144.0,"raw_peak_contact_force":0.55077,"tcp_end":[0.49845,0.09794,0.04558],"tcp_start":[0.49937,0.10218,0.06798],"tcp_to_object_dist_end":0.03304,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49807,-0.04304,0.02409],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.04029,"object_to_goal_dist_start":0.14758,"object_z_max":0.04216,"peak_contact_force":557.84654,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3417.0,"raw_peak_contact_force":1248.36712,"subtask_id":"push_progress","tcp_end":[0.51335,0.08284,0.04927],"tcp_start":[0.49845,0.09794,0.04558],"tcp_to_object_dist_end":0.12927,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49834,-0.04787,0.02418],"object_pos_start":[0.49807,-0.04304,0.02409],"object_to_goal_dist_end":0.03585,"object_to_goal_dist_start":0.04029,"object_z_max":0.02427,"peak_contact_force":445.15875,"phase_name":"lift_away","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":2970.0,"raw_peak_contact_force":1049.65687,"tcp_end":[0.51423,0.09832,0.05022],"tcp_start":[0.51335,0.08284,0.04927],"tcp_to_object_dist_end":0.14935,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37363,"average_solve_count":182.0,"average_success_count":182.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.06479,"descend_to_peg.descend_speed":0.06788,"lift_away.lift_speed":0.05003,"push_channel.push_speed":0.07268},"optimized_scores":{"best_composite_score":0.54822,"best_fitness_score":0.80822,"best_task_score":0.83883},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.55104,0.11977,0.05959],"force_p95":877.39978,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":886.7479,"mean_force":706.31503,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.52617,0.14401,0.00833]},{"body_a":"attachment","body_b":"world","contact_count":37.0,"contact_point_centroid":[0.52904,0.15556,-0.00022],"force_p95":675.72887,"geom_a":"pusher_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":771.77274,"mean_force":348.48012,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.52832,0.14643,0.00701]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":259.0,"contact_point_centroid":[0.52501,0.11994,0.04516],"force_p95":194.65378,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":498.70968,"mean_force":174.96925,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.52911,0.12437,0.03508]},{"body_a":"world","body_b":"link7","contact_count":901.0,"contact_point_centroid":[0.51298,0.19774,-5e-05],"force_p95":284.91235,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":450.97147,"mean_force":252.64382,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.525,0.13016,0.03755]},{"body_a":"world","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.51278,0.19212,-3e-05],"force_p95":216.74473,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":242.82353,"mean_force":125.15133,"phase_index":3.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.53026,0.12439,0.03553]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.50572,0.12579,0.04787],"force_p95":185.97401,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":188.07133,"mean_force":121.26996,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50659,0.13746,0.04517]},{"body_a":"peg","body_b":"channel_base_body","contact_count":939.0,"contact_point_centroid":[0.503,-0.03451,0.0082],"force_p95":0.88903,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":184.3065,"mean_force":1.352,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.52487,0.13069,0.03685]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":992.0,"contact_point_centroid":[0.52501,0.11994,0.0474],"force_p95":127.60099,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":155.54786,"mean_force":102.14363,"phase_index":3.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.52741,0.12673,0.03802]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":24.0,"contact_point_centroid":[0.52502,-0.06366,0.02457],"force_p95":8.80103,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.18285,"mean_force":3.6696,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.52197,0.13261,0.04171]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":7.0,"contact_point_centroid":[0.47497,-0.0047,0.04088],"force_p95":3.57939,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.0105,"mean_force":1.91929,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.52474,0.14315,0.01842]},{"body_a":"peg","body_b":"channel_base_body","contact_count":108.0,"contact_point_centroid":[0.50384,0.11096,0.00942],"force_p95":0.61854,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.47755,"mean_force":0.56803,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50302,0.14273,0.05849]},{"body_a":"peg","body_b":"channel_base_body","contact_count":746.0,"contact_point_centroid":[0.50354,0.11167,0.00938],"force_p95":0.60665,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55452,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50214,0.17115,0.18057]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.5031,0.12974,0.05884],"force_p95":1.7996,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.033,"mean_force":0.79874,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50125,0.14175,0.04917]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50192,-0.03986,0.00805],"force_p95":0.69709,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69709,"mean_force":0.60589,"phase_index":3.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.5274,0.12673,0.03802]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.4998,0.19942,0.29898]}],"total_contact_groups":15},"final_pose_error":0.23116,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50257,-0.03984,0.02414],"final_tcp_position":[0.52391,0.12793,0.04186],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":886.7479,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":768.0,"n_steps_budget":1000.0,"object_pos_end":[0.50374,0.11179,0.03399],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19192,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.49633,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":762.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_peg","tcp_end":[0.5059,0.14413,0.0688],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04756,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":108.0,"n_steps_budget":600.0,"object_pos_end":[0.50375,0.11162,0.03384],"object_pos_start":[0.50374,0.11179,0.03399],"object_to_goal_dist_end":0.19175,"object_to_goal_dist_start":0.19192,"object_z_max":0.03399,"peak_contact_force":0.62248,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":112.0,"raw_peak_contact_force":2.47755,"tcp_end":[0.50112,0.14165,0.04821],"tcp_start":[0.5059,0.14413,0.0688],"tcp_to_object_dist_end":0.0334,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50272,-0.03987,0.02414],"object_pos_start":[0.50375,0.11162,0.03384],"object_to_goal_dist_end":0.04324,"object_to_goal_dist_start":0.19175,"object_z_max":0.04492,"peak_contact_force":190.96972,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2179.0,"raw_peak_contact_force":886.7479,"subtask_id":"push_progress","tcp_end":[0.53025,0.1244,0.0355],"tcp_start":[0.50112,0.14165,0.04821],"tcp_to_object_dist_end":0.16694,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50257,-0.03984,0.02414],"object_pos_start":[0.50272,-0.03987,0.02414],"object_to_goal_dist_end":0.04325,"object_to_goal_dist_start":0.04324,"object_z_max":0.02414,"peak_contact_force":106.13639,"phase_name":"lift_away","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1997.0,"raw_peak_contact_force":242.82353,"tcp_end":[0.52391,0.12793,0.04186],"tcp_start":[0.53025,0.1244,0.0355],"tcp_to_object_dist_end":0.17004,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.0,"average_solve_count":210.0,"average_success_count":210.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.05639,"descend_to_peg.descend_speed":0.06136,"lift_away.lift_speed":0.04649,"push_channel.push_speed":0.0408},"optimized_scores":{"best_composite_score":0.49704,"best_fitness_score":0.75704,"best_task_score":0.6463},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.54666,0.11951,0.0587],"force_p95":1286.40214,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1305.86623,"mean_force":850.25137,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51878,0.1309,0.01602]},{"body_a":"attachment","body_b":"world","contact_count":29.0,"contact_point_centroid":[0.51878,0.15316,-0.00094],"force_p95":724.25356,"geom_a":"pusher_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":747.06687,"mean_force":355.85854,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51772,0.14454,0.00625]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52501,0.11998,0.01677],"force_p95":704.14746,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":716.26633,"mean_force":595.07763,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51959,0.13046,0.01482]},{"body_a":"world","body_b":"link7","contact_count":902.0,"contact_point_centroid":[0.50113,0.19108,-5e-05],"force_p95":286.08893,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":474.85977,"mean_force":262.50221,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50319,0.12966,0.04893]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":887.0,"contact_point_centroid":[0.47169,0.11992,0.05998],"force_p95":275.89317,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":283.92812,"mean_force":196.52729,"phase_index":3.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.50902,0.08614,0.06148]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":214.0,"contact_point_centroid":[0.52505,0.09213,0.06],"force_p95":208.09272,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":212.5171,"mean_force":186.92873,"phase_index":3.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.51366,0.08863,0.0592]},{"body_a":"peg","body_b":"channel_base_body","contact_count":941.0,"contact_point_centroid":[0.49884,-0.04391,0.00848],"force_p95":1.39538,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":70.69598,"mean_force":0.82802,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50359,0.13016,0.04763]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.49662,0.13301,0.04226],"force_p95":59.188,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":70.6812,"mean_force":21.61179,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49634,0.1446,0.03883]},{"body_a":"world","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.49905,0.1811,-2e-05],"force_p95":64.10899,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":65.21888,"mean_force":55.70024,"phase_index":3.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.50452,0.12137,0.05057]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":33.0,"contact_point_centroid":[0.47498,-0.03397,0.0241],"force_p95":5.26767,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.64291,"mean_force":3.30271,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50131,0.13125,0.05097]},{"body_a":"peg","body_b":"channel_base_body","contact_count":397.0,"contact_point_centroid":[0.49661,0.11438,0.00952],"force_p95":1.74456,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.21427,"mean_force":0.69414,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48693,0.14907,0.05151]},{"body_a":"attachment","body_b":"peg","contact_count":75.0,"contact_point_centroid":[0.49369,0.13661,0.05949],"force_p95":1.86081,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.76506,"mean_force":1.00685,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48981,0.14853,0.0441]},{"body_a":"peg","body_b":"channel_base_body","contact_count":746.0,"contact_point_centroid":[0.49623,0.11908,0.00945],"force_p95":0.6159,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.549,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49073,0.17454,0.18059]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.52504,-0.0521,0.05205],"force_p95":1.25842,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.66233,"mean_force":0.48295,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50204,0.13562,0.05001]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49953,0.19924,0.29792]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49953,-0.05141,0.00804],"force_p95":0.68341,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68341,"mean_force":0.60588,"phase_index":3.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.50833,0.08806,0.06089]}],"total_contact_groups":16},"final_pose_error":0.18786,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49989,-0.05134,0.02413],"final_tcp_position":[0.51372,0.08893,0.05898],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":1305.86623,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":771.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.11926,0.03385],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.1994,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.48513,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":770.0,"raw_peak_contact_force":2.24822,"subtask_id":"reach_peg","tcp_end":[0.48358,0.15093,0.06938],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04919,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":397.0,"n_steps_budget":600.0,"object_pos_end":[0.4961,0.11841,0.03483],"object_pos_start":[0.49602,0.11926,0.03385],"object_to_goal_dist_end":0.19852,"object_to_goal_dist_start":0.1994,"object_z_max":0.03487,"peak_contact_force":0.79674,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":472.0,"raw_peak_contact_force":3.21427,"tcp_end":[0.49122,0.14835,0.04109],"tcp_start":[0.48358,0.15093,0.06938],"tcp_to_object_dist_end":0.03097,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49918,-0.05147,0.02413],"object_pos_start":[0.4961,0.11841,0.03483],"object_to_goal_dist_end":0.03266,"object_to_goal_dist_start":0.19852,"object_z_max":0.04219,"peak_contact_force":261.54183,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1933.0,"raw_peak_contact_force":1305.86623,"subtask_id":"push_progress","tcp_end":[0.50451,0.12138,0.05057],"tcp_start":[0.49122,0.14835,0.04109],"tcp_to_object_dist_end":0.17495,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49989,-0.05134,0.02413],"object_pos_start":[0.49918,-0.05147,0.02413],"object_to_goal_dist_end":0.03276,"object_to_goal_dist_start":0.03266,"object_z_max":0.02413,"peak_contact_force":263.91437,"phase_name":"lift_away","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":2106.0,"raw_peak_contact_force":283.92812,"tcp_end":[0.51372,0.08893,0.05898],"tcp_start":[0.50451,0.12138,0.05057],"tcp_to_object_dist_end":0.1452,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```