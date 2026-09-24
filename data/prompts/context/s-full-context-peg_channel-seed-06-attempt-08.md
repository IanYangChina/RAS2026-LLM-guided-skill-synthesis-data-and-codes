## Search State

- **Seed**: 6
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → align → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 16 | -0.6792 | 0.00 | ❌ rejected |
| 7 | approach → descend → align → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 17 | -0.6617 | 0.04 | ❌ rejected |
| 6 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 10 | 0.0600 | 0.36 | ❌ rejected |
| 5 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 13 | -0.1303 | 0.39 | ❌ rejected |
| 4 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 13 | -0.3173 | 0.15 | ❌ rejected |

**Proposal policy**: task_score is 0.00 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.679) — your mutation base

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

- **Composite score**: -0.679
- **task_score** (E): 0.000
- **fitness_score**: 0.011  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.890

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 0.00 | 1.00 | 0.1364 |
| descend | 0.00 | 1.00 | 0.0391 |
| align_tcp | 0.00 | 1.00 | 0.0493 |
| contact_engage | 1.00 | 1.00 | 0.0000 |
| push_through | 0.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 0.00 / step_budget | (0.500, 0.200, 0.300)→(0.558, 0.215, 0.226) | (0.500, 0.099, 0.040)→(0.498, 0.115, 0.028) | 0.180→0.196 | 1.00 / 2.333 | 538.381 | 1158.415 |
| descend | descend | 0.00 / step_budget | (0.558, 0.215, 0.226)→(0.552, 0.214, 0.237) | (0.498, 0.115, 0.028)→(0.507, 0.117, 0.027) | 0.196→0.198 | 1.00 / 2.000 | 359.658 | 449.105 |
| align_tcp | align | 0.00 / step_budget | (0.552, 0.214, 0.237)→(0.539, 0.173, 0.223) | (0.507, 0.117, 0.027)→(0.518, 0.120, 0.027) | 0.198→0.202 | 1.00 / 2.333 | 186.031 | 1064.418 |
| contact_engage | contact | 1.00 / force_exceeded | (0.539, 0.173, 0.223)→(0.539, 0.173, 0.223) | (0.518, 0.120, 0.027)→(0.518, 0.120, 0.027) | 0.202→0.202 | 1.00 / 2.333 | 108.717 | 108.717 |
| push_through | push | 0.00 / guard_failure | (0.539, 0.173, 0.223)→(0.539, 0.173, 0.223) | (0.518, 0.120, 0.027)→(0.518, 0.120, 0.027) | 0.202→0.202 | 1.00 / 2.333 | 85.024 | 98.257 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.000
- phase_score: 0.024
- phase_breakdown.behind_peg_score: 0.081
- phase_breakdown.insertion_progress_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.015
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.678
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.295


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7549,"average_solve_count":102.0,"average_success_count":102.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_tcp.align_offset_x":-0.00298,"align_tcp.align_offset_y":-0.01196,"align_tcp.align_speed":0.04772,"align_tcp.align_tolerance":0.00556,"approach.approach_speed":0.13062,"approach.approach_tolerance":0.00873,"contact_engage.contact_force_threshold":3.79792,"contact_engage.contact_offset_y":-0.00729,"contact_engage.contact_speed":0.02037,"descend.descend_speed":0.0716,"descend.descend_tolerance":0.00772,"descend.descend_z_offset":0.01442,"push_through.push_max_time":3.60545,"push_through.push_offset_x":0.01334,"push_through.push_offset_y":0.00257,"push_through.push_speed":0.03389},"optimized_scores":{"best_composite_score":-0.68368,"best_fitness_score":0.00632,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link6","contact_count":46.0,"contact_point_centroid":[0.47454,0.1188,0.05949],"force_p95":975.01873,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1055.98299,"mean_force":478.99468,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.43984,0.26253,0.19687]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":397.0,"contact_point_centroid":[0.52503,0.11997,0.05988],"force_p95":653.09372,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":979.88519,"mean_force":571.65369,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.4974,0.16413,0.27539]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":951.0,"contact_point_centroid":[0.53677,0.11913,0.05988],"force_p95":608.21812,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":719.92144,"mean_force":503.44483,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49964,0.12307,0.27888]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":953.0,"contact_point_centroid":[0.55498,0.09013,0.05991],"force_p95":447.53418,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":526.90354,"mean_force":321.75662,"phase_index":2.0,"phase_name":"align_tcp","phase_type":"align","tcp_position_centroid":[0.51212,0.11056,0.26879]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.55499,0.06233,0.05997],"force_p95":166.49412,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":166.49412,"mean_force":166.49412,"phase_index":3.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.52563,0.11486,0.25589]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.55499,0.06208,0.05997],"force_p95":112.39637,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":114.63517,"mean_force":94.52397,"phase_index":4.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.52573,0.11475,0.25585]},{"body_a":"peg","body_b":"channel_base_body","contact_count":542.0,"contact_point_centroid":[0.50305,0.06751,0.00934],"force_p95":0.55556,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56252,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48704,0.1787,0.25647]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50307,0.06745,0.00938],"force_p95":0.55058,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55092,"mean_force":0.54665,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49966,0.12308,0.27888]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50306,0.06744,0.00938],"force_p95":0.55055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5506,"mean_force":0.54665,"phase_index":2.0,"phase_name":"align_tcp","phase_type":"align","tcp_position_centroid":[0.51234,0.11086,0.26878]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.49047,0.06948,0.00938],"force_p95":0.54997,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55054,"mean_force":0.54703,"phase_index":4.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.52573,0.11475,0.25585]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50288,0.04948,0.00938],"force_p95":0.54736,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54736,"mean_force":0.54736,"phase_index":3.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.52563,0.11486,0.25589]}],"total_contact_groups":11},"final_pose_error":0.41537,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50306,0.0675,0.0338],"final_tcp_position":[0.5258,0.11467,0.25584],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":1055.98299,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":558.0,"n_steps_budget":690.0,"object_pos_end":[0.50309,0.06745,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":652.67109,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":985.0,"raw_peak_contact_force":1055.98299,"subtask_id":"behind_peg","tcp_end":[0.482,0.10709,0.28279],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.25301,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50307,0.06743,0.0338],"object_pos_start":[0.50309,0.06745,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14762,"object_z_max":0.0338,"peak_contact_force":454.44294,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1951.0,"raw_peak_contact_force":719.92144,"subtask_id":"behind_peg","tcp_end":[0.51974,0.12738,0.27336],"tcp_start":[0.482,0.10709,0.28279],"tcp_to_object_dist_end":0.24751,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50304,0.06742,0.0338],"object_pos_start":[0.50307,0.06743,0.0338],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":1.39824,"phase_name":"align_tcp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1953.0,"raw_peak_contact_force":526.90354,"subtask_id":"behind_peg","tcp_end":[0.52563,0.11486,0.25589],"tcp_start":[0.51974,0.12738,0.27336],"tcp_to_object_dist_end":0.22823,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50302,0.06743,0.0338],"object_pos_start":[0.50304,0.06742,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14758,"object_z_max":0.0338,"peak_contact_force":166.49412,"phase_name":"contact_engage","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":166.49412,"tcp_end":[0.52569,0.11481,0.25586],"tcp_start":[0.52563,0.11486,0.25589],"tcp_to_object_dist_end":0.22819,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.503,0.06745,0.0338],"object_pos_start":[0.50302,0.06743,0.0338],"object_to_goal_dist_end":0.14761,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":77.79234,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":8.0,"raw_peak_contact_force":114.63517,"subtask_id":"insertion_progress","tcp_end":[0.5258,0.11467,0.25584],"tcp_start":[0.52578,0.1147,0.25584],"tcp_to_object_dist_end":0.22815,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.23077,"average_solve_count":104.0,"average_success_count":104.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_tcp.align_offset_x":-0.00233,"align_tcp.align_offset_y":0.00166,"align_tcp.align_speed":0.03252,"align_tcp.align_tolerance":0.00674,"approach.approach_speed":0.09886,"approach.approach_tolerance":0.00746,"contact_engage.contact_force_threshold":10.67542,"contact_engage.contact_offset_y":-0.0021,"contact_engage.contact_speed":0.02262,"descend.descend_speed":0.02503,"descend.descend_tolerance":0.00389,"descend.descend_z_offset":-0.00476,"push_through.push_max_time":5.20419,"push_through.push_offset_x":-0.00331,"push_through.push_offset_y":-0.00529,"push_through.push_speed":0.0165},"optimized_scores":{"best_composite_score":-0.67847,"best_fitness_score":0.01153,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link6","contact_count":388.0,"contact_point_centroid":[0.52512,0.11994,0.05964],"force_p95":569.12476,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1206.85258,"mean_force":497.83697,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.56454,0.26322,0.20362]},{"body_a":"world","body_b":"link6","contact_count":900.0,"contact_point_centroid":[0.62865,0.23077,-7e-05],"force_p95":464.86464,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1154.71254,"mean_force":272.01422,"phase_index":2.0,"phase_name":"align_tcp","phase_type":"align","tcp_position_centroid":[0.56727,0.2221,0.21824]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":367.0,"contact_point_centroid":[0.55473,0.11996,0.04846],"force_p95":250.63834,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":903.66884,"mean_force":202.09047,"phase_index":2.0,"phase_name":"align_tcp","phase_type":"align","tcp_position_centroid":[0.55461,0.20308,0.21452]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":999.0,"contact_point_centroid":[0.525,0.11999,0.05996],"force_p95":265.60519,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":268.97486,"mean_force":217.17936,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.59764,0.26668,0.2012]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.63013,0.22667,-4e-05],"force_p95":95.16483,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":95.16483,"mean_force":95.16483,"phase_index":3.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.55212,0.20399,0.21411]},{"body_a":"world","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.63013,0.22667,-4e-05],"force_p95":90.76654,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":91.07337,"mean_force":89.09706,"phase_index":4.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.55212,0.20398,0.21411]},{"body_a":"peg","body_b":"channel_base_body","contact_count":455.0,"contact_point_centroid":[0.5144,0.11869,0.00967],"force_p95":31.88906,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.44337,"mean_force":8.77548,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.54759,0.25522,0.19867]},{"body_a":"peg","body_b":"link6","contact_count":388.0,"contact_point_centroid":[0.51951,0.12118,0.05912],"force_p95":32.47873,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.38975,"mean_force":9.692,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.56454,0.26322,0.20362]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.55498,0.11995,0.0486],"force_p95":29.84408,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":29.84437,"mean_force":29.43818,"phase_index":4.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.55212,0.20398,0.21411]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.55498,0.11996,0.0486],"force_p95":25.32607,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":25.32607,"mean_force":25.32607,"phase_index":3.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.55212,0.20399,0.21411]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50117,0.11426,0.00942],"force_p95":0.62591,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.71667,"mean_force":0.54631,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.59765,0.26669,0.20119]},{"body_a":"peg","body_b":"link6","contact_count":5.0,"contact_point_centroid":[0.52048,0.12614,0.05934],"force_p95":1.16999,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.20138,"mean_force":0.50685,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.60841,0.27088,0.19166]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.501,0.11404,0.00943],"force_p95":0.60101,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66415,"mean_force":0.54159,"phase_index":2.0,"phase_name":"align_tcp","phase_type":"align","tcp_position_centroid":[0.5708,0.22851,0.21792]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.51651,0.10918,0.0094],"force_p95":0.6,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60255,"mean_force":0.57184,"phase_index":4.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.55212,0.20398,0.21411]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50122,0.19848,0.29669]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.48438,0.12,0.00942],"force_p95":0.47884,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47884,"mean_force":0.47884,"phase_index":3.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.55212,0.20399,0.21411]}],"total_contact_groups":16},"final_pose_error":0.48009,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50107,0.11406,0.03385],"final_tcp_position":[0.55212,0.20396,0.21411],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":1206.85258,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":477.0,"n_steps_budget":750.0,"object_pos_end":[0.50252,0.11683,0.03621],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19688,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":437.97123,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1247.0,"raw_peak_contact_force":1206.85258,"subtask_id":"behind_peg","tcp_end":[0.60836,0.27083,0.19156],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.24301,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50102,0.11424,0.03388],"object_pos_start":[0.50252,0.11683,0.03621],"object_to_goal_dist_end":0.19434,"object_to_goal_dist_start":0.19688,"object_z_max":0.03621,"peak_contact_force":268.80758,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2004.0,"raw_peak_contact_force":268.97486,"subtask_id":"behind_peg","tcp_end":[0.58418,0.2579,0.21471],"tcp_start":[0.60836,0.27083,0.19156],"tcp_to_object_dist_end":0.24546,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50102,0.11417,0.03386],"object_pos_start":[0.50102,0.11424,0.03388],"object_to_goal_dist_end":0.19427,"object_to_goal_dist_start":0.19434,"object_z_max":0.03415,"peak_contact_force":245.64141,"phase_name":"align_tcp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2267.0,"raw_peak_contact_force":1154.71254,"subtask_id":"behind_peg","tcp_end":[0.55212,0.20399,0.21411],"tcp_start":[0.58418,0.2579,0.21471],"tcp_to_object_dist_end":0.20777,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50107,0.11414,0.03385],"object_pos_start":[0.50102,0.11417,0.03386],"object_to_goal_dist_end":0.19424,"object_to_goal_dist_start":0.19427,"object_z_max":0.03386,"peak_contact_force":95.16483,"phase_name":"contact_engage","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":95.16483,"tcp_end":[0.55212,0.20399,0.21411],"tcp_start":[0.55212,0.20399,0.21411],"tcp_to_object_dist_end":0.20777,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.50109,0.11411,0.03385],"object_pos_start":[0.50107,0.11414,0.03385],"object_to_goal_dist_end":0.19421,"object_to_goal_dist_start":0.19424,"object_z_max":0.03385,"peak_contact_force":88.21602,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":12.0,"raw_peak_contact_force":91.07337,"subtask_id":"insertion_progress","tcp_end":[0.55212,0.20396,0.21411],"tcp_start":[0.55212,0.20396,0.21411],"tcp_to_object_dist_end":0.20777,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44643,"average_solve_count":112.0,"average_success_count":112.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_tcp.align_offset_x":0.00063,"align_tcp.align_offset_y":-0.00863,"align_tcp.align_speed":0.03986,"align_tcp.align_tolerance":0.00528,"approach.approach_speed":0.0729,"approach.approach_tolerance":0.006,"contact_engage.contact_force_threshold":6.25129,"contact_engage.contact_offset_y":0.0083,"contact_engage.contact_speed":0.01671,"descend.descend_speed":0.06546,"descend.descend_tolerance":0.0078,"descend.descend_z_offset":0.00271,"push_through.push_max_time":5.03567,"push_through.push_offset_x":0.00502,"push_through.push_offset_y":-0.01832,"push_through.push_speed":0.02384},"optimized_scores":{"best_composite_score":-0.67539,"best_fitness_score":0.01461,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":867.0,"contact_point_centroid":[0.63635,0.22767,-8e-05],"force_p95":361.58053,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1511.63758,"mean_force":302.63036,"phase_index":2.0,"phase_name":"align_tcp","phase_type":"align","tcp_position_centroid":[0.55022,0.23088,0.20671]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":424.0,"contact_point_centroid":[0.52513,0.11995,0.05963],"force_p95":582.54058,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1212.40904,"mean_force":506.83778,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.55116,0.26215,0.20655]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":18.0,"contact_point_centroid":[0.52501,0.12,0.05996],"force_p95":713.23317,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":735.81709,"mean_force":643.34262,"phase_index":2.0,"phase_name":"align_tcp","phase_type":"align","tcp_position_centroid":[0.55349,0.26221,0.21941]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.52501,0.11999,0.05995],"force_p95":340.14989,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":358.418,"mean_force":270.88113,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.56841,0.2637,0.21367]},{"body_a":"peg","body_b":"link6","contact_count":84.0,"contact_point_centroid":[0.50382,0.11949,0.05817],"force_p95":70.38578,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":345.05929,"mean_force":33.06708,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.46182,0.27189,0.17358]},{"body_a":"peg","body_b":"channel_base_body","contact_count":171.0,"contact_point_centroid":[0.48735,0.11961,0.00937],"force_p95":59.66124,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":343.81351,"mean_force":17.35407,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.46861,0.24719,0.17643]},{"body_a":"world","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.64169,0.22691,-0.00035],"force_p95":87.80511,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":89.0633,"mean_force":81.33315,"phase_index":4.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.53811,0.19976,0.20008]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.64166,0.2269,-0.00037],"force_p95":64.49192,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":64.49192,"mean_force":64.49192,"phase_index":3.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.5381,0.19979,0.20007]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":110.0,"contact_point_centroid":[0.47429,0.11977,0.01534],"force_p95":28.22939,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.18462,"mean_force":9.64855,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49948,0.25575,0.21789]},{"body_a":"peg","body_b":"world","contact_count":1000.0,"contact_point_centroid":[0.54034,0.17478,-0.00192],"force_p95":0.87494,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.2364,"mean_force":1.21108,"phase_index":2.0,"phase_name":"align_tcp","phase_type":"align","tcp_position_centroid":[0.55432,0.23989,0.20516]},{"body_a":"peg","body_b":"link6","contact_count":55.0,"contact_point_centroid":[0.56726,0.15466,0.02431],"force_p95":22.27644,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.6727,"mean_force":11.16103,"phase_index":2.0,"phase_name":"align_tcp","phase_type":"align","tcp_position_centroid":[0.54871,0.23002,0.20829]},{"body_a":"peg","body_b":"world","contact_count":314.0,"contact_point_centroid":[0.48691,0.15604,-0.00156],"force_p95":0.99523,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.87061,"mean_force":0.62199,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.5747,0.25959,0.21416]},{"body_a":"peg","body_b":"world","contact_count":1.0,"contact_point_centroid":[0.54787,0.15368,-0.00198],"force_p95":0.72584,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72584,"mean_force":0.72584,"phase_index":3.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.5381,0.19979,0.20007]},{"body_a":"peg","body_b":"world","contact_count":4.0,"contact_point_centroid":[0.54857,0.16615,-0.00199],"force_p95":0.71253,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72584,"mean_force":0.60603,"phase_index":4.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.53811,0.19976,0.20008]},{"body_a":"peg","body_b":"world","contact_count":1000.0,"contact_point_centroid":[0.49874,0.16434,-0.00196],"force_p95":0.68387,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68388,"mean_force":0.6062,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.56841,0.2637,0.21367]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":7.0,"contact_point_centroid":[0.47474,0.11979,0.05962],"force_p95":0.0,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.39113,0.25929,0.11628]}],"total_contact_groups":16},"final_pose_error":0.46914,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.54933,0.17869,0.01409],"final_tcp_position":[0.53813,0.19972,0.20012],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":1511.63758,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":511.0,"n_steps_budget":990.0,"object_pos_end":[0.48697,0.16136,0.01413],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.24309,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":524.50137,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1110.0,"raw_peak_contact_force":1212.40904,"subtask_id":"behind_peg","tcp_end":[0.58361,0.26768,0.20486],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.23879,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51659,0.16882,0.01413],"object_pos_start":[0.48697,0.16136,0.01413],"object_to_goal_dist_end":0.25071,"object_to_goal_dist_start":0.24309,"object_z_max":0.01413,"peak_contact_force":355.72408,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2000.0,"raw_peak_contact_force":358.418,"subtask_id":"behind_peg","tcp_end":[0.55249,0.25685,0.22271],"tcp_start":[0.58361,0.26768,0.20486],"tcp_to_object_dist_end":0.22922,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54933,0.17859,0.01409],"object_pos_start":[0.51659,0.16882,0.01413],"object_to_goal_dist_end":0.26453,"object_to_goal_dist_start":0.25071,"object_z_max":0.01566,"peak_contact_force":311.05482,"phase_name":"align_tcp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1940.0,"raw_peak_contact_force":1511.63758,"subtask_id":"behind_peg","tcp_end":[0.5381,0.19979,0.20007],"tcp_start":[0.55249,0.25685,0.22271],"tcp_to_object_dist_end":0.18752,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.54933,0.17857,0.01409],"object_pos_start":[0.54933,0.17859,0.01409],"object_to_goal_dist_end":0.2645,"object_to_goal_dist_start":0.26453,"object_z_max":0.01409,"peak_contact_force":64.49192,"phase_name":"contact_engage","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":64.49192,"tcp_end":[0.5381,0.19977,0.20006],"tcp_start":[0.5381,0.19979,0.20007],"tcp_to_object_dist_end":0.18751,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.54933,0.17857,0.0141],"object_pos_start":[0.54933,0.17857,0.01409],"object_to_goal_dist_end":0.26451,"object_to_goal_dist_start":0.2645,"object_z_max":0.0141,"peak_contact_force":89.0633,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":8.0,"raw_peak_contact_force":89.0633,"subtask_id":"insertion_progress","tcp_end":[0.53813,0.19972,0.20012],"tcp_start":[0.53812,0.19974,0.2001],"tcp_to_object_dist_end":0.18756,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```