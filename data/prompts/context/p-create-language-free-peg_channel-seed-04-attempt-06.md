## Search State

- **Seed**: 4
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | force_exceeded | pose_tolerance | 7 | -0.1008 | 0.42 | ❌ rejected |
| 5 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.1724 | 0.18 | ❌ rejected |
| 4 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.2795 | 0.40 | ❌ rejected |
| 3 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.2542 | 0.58 | ❌ rejected |
| 2 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.3784 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.42 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`
- Frozen object start: [0.5354444884457894, 0.08090620422514894, 0.04]
- Frozen task target: [0.5354444884457894, -0.07909379577485107, 0.04]
- Goal object position: (0.5354444884457894, -0.07909379577485107, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5354444884457894, 0.08090620422514894, 0.04)
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
  frozen_object_start: [0.5354, 0.0809, 0.04]
  frozen_task_target: [0.5354, -0.0791, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5354444884457894, 0.08090620422514894, 0.04]}
  frozen_targets: {'channel_exit': [0.5354444884457894, -0.07909379577485107, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c

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
| `object` | offset from object initial position (0.5354444884457894, 0.08090620422514894, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5354444884457894, -0.07909379577485107, 0.04) | final destination targets |
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

## Current Skill (Q=-0.101) — your mutation base

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
- id: reach_goal
  offset:
  - 0.0
  - -0.03
  - 0.0
  weight: 0.7
phases:
- id: approach_1
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
    - 0.05
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_peg
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.03
    - -0.01
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 0.5
      - 5.0
      default: 2.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_peg
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
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.19
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
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
    threshold: 35.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: reach_goal
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, 0.05], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, -0.01]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.19, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=35.0
  - retries: max_attempts=1, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.101
- **task_score** (E): 0.423
- **fitness_score**: 0.206  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.133
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1829 |
| descend_1 | 0.00 | 1.00 | 0.0927 |
| align_1 | 1.00 | 1.00 | 0.0041 |
| push_1 | 1.00 | 1.00 | 0.0404 |
| retract_1 | 1.00 | 1.00 | 0.1671 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.516, 0.141, 0.129) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.164 | 1.00 / 1.000 | 0.550 | 3.242 |
| descend_1 | descend | 0.00 / step_budget | (0.516, 0.141, 0.129)→(0.502, 0.134, 0.038) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.164→0.165 | 1.00 / 1.000 | 0.544 | 0.560 |
| align_1 | align | 1.00 / step_budget | (0.502, 0.134, 0.038)→(0.499, 0.134, 0.035) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.165 | 1.00 / 1.000 | 0.540 | 0.559 |
| push_1 | push | 1.00 / force_exceeded | (0.499, 0.134, 0.035)→(0.496, 0.094, 0.030) | (0.505, 0.084, 0.034)→(0.507, 0.065, 0.036) | 0.165→0.146 | 1.00 / 2.333 | 2614.223 | 4.843 |
| retract_1 | retract | 1.00 / step_budget | (0.496, 0.094, 0.030)→(0.496, -0.064, 0.085) | (0.507, 0.065, 0.036)→(0.505, -0.021, 0.024) | 0.146→0.062 | 1.00 / 1.000 | 0.582 | 24.474 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.674
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.348
- phase_score: 0.046
- phase_breakdown.reach_peg_score: 0.116
- phase_breakdown.reach_goal_score: 0.017

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.353
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.752
- **Median Q (composite search score)**: -0.087
- **K-run variance**: 0.0009
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.321


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `424e8a040c59c1e1e42822c1022320b6050001458f7b9b4937cb9238911ce80b`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `72d2436204c0f1ee3bbdbdfe3e5489661153a48f95d8f0dc3b73e6ce1e1e081b`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.70886,"average_solve_count":237.0,"average_success_count":237.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_x_offset":-0.01512,"approach_1.approach_height":0.07727,"descend_1.contact_force":2.37297,"descend_1.speed":0.01611,"push_1.push_force_threshold":27.80365,"push_1.push_speed":0.04488,"retract_1.retract_height":0.06755},"optimized_scores":{"best_composite_score":-0.14264,"best_fitness_score":0.09736,"best_task_score":0.1681},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":129.0,"contact_point_centroid":[0.50008,0.05955,0.04184],"force_p95":18.53875,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.20228,"mean_force":6.13238,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49498,0.07022,0.04203]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":127.0,"contact_point_centroid":[0.52512,0.04432,0.02924],"force_p95":13.5291,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.05052,"mean_force":3.93316,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49483,0.06817,0.0426]},{"body_a":"peg","body_b":"channel_base_body","contact_count":390.0,"contact_point_centroid":[0.50663,0.00482,0.00873],"force_p95":13.33499,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.79534,"mean_force":2.31802,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4955,0.00804,0.06687]},{"body_a":"peg","body_b":"channel_base_body","contact_count":299.0,"contact_point_centroid":[0.50634,0.07717,0.00947],"force_p95":3.51044,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.56538,"mean_force":0.94905,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4974,0.11748,0.03151]},{"body_a":"peg","body_b":"channel_base_body","contact_count":318.0,"contact_point_centroid":[0.50546,0.08091,0.00934],"force_p95":0.57678,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.59475,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51445,0.1673,0.21094]},{"body_a":"attachment","body_b":"peg","contact_count":54.0,"contact_point_centroid":[0.50241,0.09614,0.04642],"force_p95":3.98109,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.26932,"mean_force":2.42653,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49708,0.10781,0.03076]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50076,0.19767,0.29379]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.525,0.07868,0.01103],"force_p95":0.73769,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.78714,"mean_force":0.44803,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49714,0.10617,0.03078]},{"body_a":"peg","body_b":"channel_base_body","contact_count":493.0,"contact_point_centroid":[0.50601,0.08089,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55023,"mean_force":0.54676,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51538,0.13425,0.08528]},{"body_a":"peg","body_b":"channel_base_body","contact_count":22.0,"contact_point_centroid":[0.50525,0.07961,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54672,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5028,0.13037,0.03709]}],"total_contact_groups":10},"final_pose_error":0.01989,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5066,-0.0077,0.0241],"final_tcp_position":[0.49662,-0.06393,0.09635],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":3919.3665,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":347.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54994,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":354.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_peg","tcp_end":[0.52853,0.13849,0.13402],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11779,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":493.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":0.54458,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":493.0,"raw_peak_contact_force":0.55023,"subtask_id":"reach_peg","tcp_end":[0.50428,0.13062,0.03833],"tcp_start":[0.52853,0.13849,0.13402],"tcp_to_object_dist_end":0.04999,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":22.0,"n_steps_budget":600.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":0.54527,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":22.0,"raw_peak_contact_force":0.55006,"subtask_id":"reach_peg","tcp_end":[0.50047,0.13017,0.03569],"tcp_start":[0.50428,0.13062,0.03833],"tcp_to_object_dist_end":0.04962,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":306.0,"n_steps_budget":1000.0,"object_pos_end":[0.50684,0.07702,0.03588],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.15722,"object_to_goal_dist_start":0.16113,"object_z_max":0.03588,"peak_contact_force":3919.3665,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":356.0,"raw_peak_contact_force":4.56538,"subtask_id":"reach_goal","tcp_end":[0.49714,0.10572,0.03078],"tcp_start":[0.50047,0.13017,0.03569],"tcp_to_object_dist_end":0.03072,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":480.0,"n_steps_budget":1000.0,"object_pos_end":[0.5066,-0.0077,0.0241],"object_pos_start":[0.50684,0.07702,0.03588],"object_to_goal_dist_end":0.07433,"object_to_goal_dist_start":0.15722,"object_z_max":0.04081,"peak_contact_force":0.56199,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":646.0,"raw_peak_contact_force":23.20228,"tcp_end":[0.49662,-0.06393,0.09635],"tcp_start":[0.49714,0.10572,0.03078],"tcp_to_object_dist_end":0.09209,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `54762c1e743ba455eff3c9979c2b42f5642abe1893e28eae37dc231d7efcd4e4`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.2948,"average_solve_count":173.0,"average_success_count":173.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_x_offset":-0.0165,"approach_1.approach_height":0.06856,"descend_1.contact_force":1.78199,"descend_1.speed":0.03899,"push_1.push_force_threshold":26.79052,"push_1.push_speed":0.02523,"retract_1.retract_height":0.05085},"optimized_scores":{"best_composite_score":-0.07282,"best_fitness_score":0.16718,"best_task_score":0.34821},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":183.0,"contact_point_centroid":[0.50002,0.06338,0.04306],"force_p95":22.43333,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.35816,"mean_force":8.17816,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49416,0.07378,0.04167]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":172.0,"contact_point_centroid":[0.52512,0.05097,0.0284],"force_p95":14.43895,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.98562,"mean_force":5.24684,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49415,0.07267,0.04197]},{"body_a":"peg","body_b":"channel_base_body","contact_count":395.0,"contact_point_centroid":[0.50672,0.01311,0.00888],"force_p95":16.40242,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.0697,"mean_force":3.88124,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49498,0.01529,0.05841]},{"body_a":"attachment","body_b":"peg","contact_count":130.0,"contact_point_centroid":[0.5015,0.11742,0.04249],"force_p95":3.84927,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.34532,"mean_force":2.05653,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49597,0.12885,0.03036]},{"body_a":"peg","body_b":"channel_base_body","contact_count":390.0,"contact_point_centroid":[0.50624,0.09798,0.00955],"force_p95":3.39062,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.19978,"mean_force":1.13118,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49611,0.13843,0.03092]},{"body_a":"peg","body_b":"channel_base_body","contact_count":315.0,"contact_point_centroid":[0.50553,0.10457,0.00936],"force_p95":0.60058,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.58225,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50928,0.17835,0.20767]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50038,0.19856,0.29454]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":61.0,"contact_point_centroid":[0.52502,0.09926,0.02631],"force_p95":1.5195,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.58329,"mean_force":0.90378,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49602,0.12701,0.03037]},{"body_a":"peg","body_b":"channel_base_body","contact_count":437.0,"contact_point_centroid":[0.50582,0.10477,0.00939],"force_p95":0.57556,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57865,"mean_force":0.54635,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50988,0.15621,0.08128]},{"body_a":"peg","body_b":"channel_base_body","contact_count":23.0,"contact_point_centroid":[0.50429,0.10304,0.00939],"force_p95":0.55187,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57566,"mean_force":0.54516,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5017,0.15363,0.03677]}],"total_contact_groups":10},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50618,-0.00325,0.02415],"final_tcp_position":[0.49645,-0.06306,0.08125],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":3920.11096,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":342.0,"n_steps_budget":1000.0,"object_pos_end":[0.50585,0.1046,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18479,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.55345,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":347.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_peg","tcp_end":[0.51878,0.1593,0.12675],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10859,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":437.0,"n_steps_budget":1000.0,"object_pos_end":[0.506,0.10464,0.03384],"object_pos_start":[0.50585,0.1046,0.03384],"object_to_goal_dist_end":0.18484,"object_to_goal_dist_start":0.18479,"object_z_max":0.03384,"peak_contact_force":0.54124,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":437.0,"raw_peak_contact_force":0.57865,"subtask_id":"reach_peg","tcp_end":[0.5033,0.15391,0.03808],"tcp_start":[0.51878,0.1593,0.12675],"tcp_to_object_dist_end":0.04953,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":23.0,"n_steps_budget":600.0,"object_pos_end":[0.50593,0.10472,0.03383],"object_pos_start":[0.506,0.10464,0.03384],"object_to_goal_dist_end":0.18492,"object_to_goal_dist_start":0.18484,"object_z_max":0.03384,"peak_contact_force":0.52981,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":23.0,"raw_peak_contact_force":0.57566,"subtask_id":"reach_peg","tcp_end":[0.49917,0.15345,0.03532],"tcp_start":[0.5033,0.15391,0.03808],"tcp_to_object_dist_end":0.04921,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":414.0,"n_steps_budget":1000.0,"object_pos_end":[0.50699,0.09609,0.03597],"object_pos_start":[0.50593,0.10472,0.03383],"object_to_goal_dist_end":0.17628,"object_to_goal_dist_start":0.18492,"object_z_max":0.03599,"peak_contact_force":3920.11096,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":581.0,"raw_peak_contact_force":4.34532,"subtask_id":"reach_goal","tcp_end":[0.49608,0.1244,0.03036],"tcp_start":[0.49917,0.15345,0.03532],"tcp_to_object_dist_end":0.03084,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":502.0,"n_steps_budget":1000.0,"object_pos_end":[0.50618,-0.00325,0.02415],"object_pos_start":[0.50699,0.09609,0.03597],"object_to_goal_dist_end":0.07861,"object_to_goal_dist_start":0.17628,"object_z_max":0.0408,"peak_contact_force":0.57025,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":750.0,"raw_peak_contact_force":28.35816,"tcp_end":[0.49645,-0.06306,0.08125],"tcp_start":[0.49608,0.1244,0.03036],"tcp_to_object_dist_end":0.08326,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b230a5798f38c3fb8968a6bc74f96ee85fe7026f3170cf8216fc868a1c5c570f`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.64,"average_solve_count":250.0,"average_success_count":250.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_x_offset":-0.00832,"approach_1.approach_height":0.0677,"descend_1.contact_force":4.14388,"descend_1.speed":0.01517,"push_1.push_force_threshold":32.38704,"push_1.push_speed":0.0358,"retract_1.retract_height":0.0501},"optimized_scores":{"best_composite_score":-0.08706,"best_fitness_score":0.35294,"best_task_score":0.75157},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":135.0,"contact_point_centroid":[0.49944,0.00896,0.04115],"force_p95":18.12947,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.86288,"mean_force":7.01537,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4935,0.01925,0.04121]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":158.0,"contact_point_centroid":[0.52517,-0.00505,0.02936],"force_p95":12.37781,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.00045,"mean_force":4.49469,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49341,0.01653,0.04219]},{"body_a":"peg","body_b":"channel_base_body","contact_count":265.0,"contact_point_centroid":[0.50528,-0.03385,0.00914],"force_p95":14.77521,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.8478,"mean_force":3.64533,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49437,-0.01478,0.05607]},{"body_a":"attachment","body_b":"peg","contact_count":658.0,"contact_point_centroid":[0.50018,0.0624,0.03939],"force_p95":4.94096,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.61808,"mean_force":2.41861,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49432,0.0736,0.0299]},{"body_a":"peg","body_b":"channel_base_body","contact_count":845.0,"contact_point_centroid":[0.50516,0.04224,0.00978],"force_p95":4.28841,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.16518,"mean_force":2.06586,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49424,0.08474,0.03015]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":468.0,"contact_point_centroid":[0.52506,0.04014,0.02569],"force_p95":2.25621,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.01729,"mean_force":1.20183,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49448,0.06711,0.02989]},{"body_a":"peg","body_b":"channel_base_body","contact_count":346.0,"contact_point_centroid":[0.50313,0.06749,0.00931],"force_p95":0.62619,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.5715,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49949,0.16228,0.20953]},{"body_a":"peg","body_b":"channel_base_body","contact_count":560.0,"contact_point_centroid":[0.50304,0.0674,0.00938],"force_p95":0.55059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55198,"mean_force":0.54665,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49812,0.12141,0.07912]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.50137,0.0677,0.00938],"force_p95":0.55038,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55058,"mean_force":0.54652,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49815,0.11706,0.03568]}],"total_contact_groups":9},"final_pose_error":0.01968,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50223,-0.05279,0.02409],"final_tcp_position":[0.49616,-0.06458,0.07849],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":21.86288,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":362.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54551,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":346.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_peg","tcp_end":[0.50008,0.12625,0.12501],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10859,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":560.0,"n_steps_budget":1000.0,"object_pos_end":[0.50301,0.06745,0.0338],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.14761,"object_to_goal_dist_start":0.14758,"object_z_max":0.0338,"peak_contact_force":0.54665,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":560.0,"raw_peak_contact_force":0.55198,"subtask_id":"reach_peg","tcp_end":[0.49894,0.11727,0.0366],"tcp_start":[0.50008,0.12625,0.12501],"tcp_to_object_dist_end":0.05006,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50304,0.0675,0.0338],"object_pos_start":[0.50301,0.06745,0.0338],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14761,"object_z_max":0.0338,"peak_contact_force":0.54562,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":20.0,"raw_peak_contact_force":0.55058,"subtask_id":"reach_peg","tcp_end":[0.49713,0.11691,0.03464],"tcp_start":[0.49894,0.11727,0.0366],"tcp_to_object_dist_end":0.04977,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50719,0.02279,0.0361],"object_pos_start":[0.50304,0.0675,0.0338],"object_to_goal_dist_end":0.10312,"object_to_goal_dist_start":0.14766,"object_z_max":0.03627,"peak_contact_force":3.19062,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1971.0,"raw_peak_contact_force":5.61808,"subtask_id":"reach_goal","tcp_end":[0.49492,0.05062,0.02986],"tcp_start":[0.49713,0.11691,0.03464],"tcp_to_object_dist_end":0.03105,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":338.0,"n_steps_budget":900.0,"object_pos_end":[0.50223,-0.05279,0.02409],"object_pos_start":[0.50719,0.02279,0.0361],"object_to_goal_dist_end":0.0316,"object_to_goal_dist_start":0.10312,"object_z_max":0.04084,"peak_contact_force":0.61462,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":558.0,"raw_peak_contact_force":21.86288,"tcp_end":[0.49616,-0.06458,0.07849],"tcp_start":[0.49492,0.05062,0.02986],"tcp_to_object_dist_end":0.05599,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```