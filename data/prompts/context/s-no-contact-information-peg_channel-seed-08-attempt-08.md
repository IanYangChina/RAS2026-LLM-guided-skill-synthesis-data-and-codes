## Search State

- **Seed**: 8
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4320 | 0.52 | ✅ accepted |
| 7 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4193 | 0.37 | ❌ rejected |
| 6 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4278 | 0.49 | ✅ accepted |
| 5 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.4293 | 0.40 | ✅ accepted |
| 4 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.4191 | 0.29 | ✅ accepted |

**Proposal policy**: task_score is 0.52 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.432) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_approach
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.1
  weight: 0.2
- id: reach_descent
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.0
  weight: 0.3
- id: reach_goal
  metric: goal_progress
  weight: 0.5
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
    - 0.05
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_approach
- id: descend_1
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
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_descent
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - -0.03
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    contact_speed:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_made
    when: after_phase
    predicate: contact_detected
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.005
    - 0.0
    - 0.0
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, -0.03, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_made, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.005, 0.0]
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.005, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.432
- **task_score** (E): 0.516
- **fitness_score**: 0.692  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1701 |
| descend_1 | 1.00 | 0.1118 |
| contact_1 | 0.33 | 0.0433 |
| push_1 | 1.00 | 0.1320 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.134, 0.147) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 |
| descend_1 | descend | 1.00 / step_budget | (0.513, 0.134, 0.147)→(0.500, 0.131, 0.037) | (0.503, 0.080, 0.034)→(0.505, 0.087, 0.031) | 0.160→0.167 |
| contact_1 | contact | 0.33 / step_budget | (0.504, 0.117, 0.036)→(0.501, 0.074, 0.033) | (0.505, 0.087, 0.031)→(0.506, 0.062, 0.037) | 0.167→0.142 |
| push_1 | push | 1.00 / step_budget | (0.501, 0.074, 0.033)→(0.496, -0.058, 0.034) | (0.503, 0.042, 0.033)→(0.503, -0.084, 0.033) | 0.123→0.012 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- terminal_score: 0.863
- phase_score: 0.845
- phase_breakdown.reach_goal_score: 0.869
- phase_breakdown.reach_approach_score: 0.821
- phase_breakdown.reach_descent_score: 0.822

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.853
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.863
- **Median Q (composite search score)**: 0.384
- **K-run variance**: 0.0136
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.380


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.15842,"average_solve_count":202.0,"average_success_count":202.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.22164,"contact_1.contact_speed":0.03004,"descend_1.descend_speed":0.02773,"push_1.push_speed":0.07404},"optimized_scores":{"best_composite_score":0.59251,"best_fitness_score":0.85251,"best_task_score":0.86315},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":1882.0,"contact_point_centroid":[0.49872,0.08411,0.00844],"force_p95":184.96067,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":241.33043,"mean_force":62.47844,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49894,0.12952,0.03336]},{"body_a":"attachment","body_b":"peg","contact_count":1314.0,"contact_point_centroid":[0.49862,0.12894,0.0366],"force_p95":204.4433,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":226.45916,"mean_force":93.39883,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49804,0.13953,0.0346]},{"body_a":"attachment","body_b":"peg","contact_count":333.0,"contact_point_centroid":[0.49814,-0.03117,0.04508],"force_p95":158.52285,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":161.82763,"mean_force":66.92408,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49707,-0.02017,0.03411]},{"body_a":"peg","body_b":"channel_base_body","contact_count":168.0,"contact_point_centroid":[0.49754,-0.10234,0.04497],"force_p95":159.04973,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":161.70005,"mean_force":128.4286,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49697,-0.04696,0.0344]},{"body_a":"attachment","body_b":"peg","contact_count":159.0,"contact_point_centroid":[0.49475,0.16042,0.04171],"force_p95":46.62977,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.13136,"mean_force":40.13153,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49218,0.17143,0.04177]},{"body_a":"peg","body_b":"world","contact_count":178.0,"contact_point_centroid":[0.50124,0.12966,-0.00042],"force_p95":37.70925,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.83827,"mean_force":23.78021,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49197,0.17112,0.04276]},{"body_a":"peg","body_b":"channel_base_body","contact_count":322.0,"contact_point_centroid":[0.49436,-0.06591,0.00987],"force_p95":9.97082,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.3209,"mean_force":3.67346,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49717,-0.01689,0.03416]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":431.0,"contact_point_centroid":[0.52558,0.11047,0.02044],"force_p95":25.76428,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.12311,"mean_force":13.70303,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50251,0.15288,0.03673]},{"body_a":"peg","body_b":"channel_base_body","contact_count":753.0,"contact_point_centroid":[0.49495,0.11936,0.00952],"force_p95":28.19429,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.84661,"mean_force":3.97785,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48708,0.16968,0.08997]},{"body_a":"peg","body_b":"world","contact_count":760.0,"contact_point_centroid":[0.5052,0.12114,-0.00011],"force_p95":27.93171,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.87744,"mean_force":11.31881,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4956,0.16476,0.03425]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":41.0,"contact_point_centroid":[0.47494,-0.05698,0.02815],"force_p95":10.15234,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.26195,"mean_force":2.60473,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4971,0.00378,0.03382]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":62.0,"contact_point_centroid":[0.47499,0.01544,0.02698],"force_p95":5.62165,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.82884,"mean_force":2.64147,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50018,0.07532,0.03388]},{"body_a":"peg","body_b":"channel_base_body","contact_count":388.0,"contact_point_centroid":[0.49633,0.11915,0.00942],"force_p95":0.62033,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.5591,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49142,0.18452,0.22058]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49945,0.19912,0.29706]}],"total_contact_groups":14},"final_pose_error":0.03013,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4941,-0.08153,0.02803],"final_tcp_position":[0.49749,-0.05051,0.03437],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"phases":[{"n_steps":413.0,"n_steps_budget":600.0,"object_pos_end":[0.49605,0.11952,0.03405],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19964,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_approach","tcp_end":[0.48465,0.17078,0.14959],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12691,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":816.0,"n_steps_budget":1000.0,"object_pos_end":[0.50185,0.14128,0.02588],"object_pos_start":[0.49605,0.11952,0.03405],"object_to_goal_dist_end":0.22173,"object_to_goal_dist_start":0.19964,"object_z_max":0.03433,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_descent","tcp_end":[0.49323,0.17383,0.03531],"tcp_start":[0.48465,0.17078,0.14959],"tcp_to_object_dist_end":0.03497,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1902.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,0.08111,0.04103],"object_pos_start":[0.50185,0.14128,0.02588],"object_to_goal_dist_end":0.16115,"object_to_goal_dist_start":0.22173,"object_z_max":0.04122,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","tcp_end":[0.50001,0.05853,0.03603],"tcp_start":[0.5045,0.13197,0.03127],"tcp_to_object_dist_end":0.02343,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":414.0,"n_steps_budget":1000.0,"object_pos_end":[0.4941,-0.08153,0.02803],"object_pos_start":[0.4963,0.02166,0.02699],"object_to_goal_dist_end":0.01343,"object_to_goal_dist_start":0.10255,"object_z_max":0.02883,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"reach_goal","tcp_end":[0.49749,-0.05051,0.03437],"tcp_start":[0.50001,0.05853,0.03603],"tcp_to_object_dist_end":0.03184,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.80769,"average_solve_count":208.0,"average_success_count":208.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.20828,"contact_1.contact_speed":0.01023,"descend_1.descend_speed":0.02884,"push_1.push_speed":0.05317},"optimized_scores":{"best_composite_score":0.38437,"best_fitness_score":0.64437,"best_task_score":0.40813},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":371.0,"contact_point_centroid":[0.50257,-0.00709,0.04761],"force_p95":105.2892,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":111.32952,"mean_force":21.6624,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49662,0.00409,0.03154]},{"body_a":"peg","body_b":"channel_base_body","contact_count":68.0,"contact_point_centroid":[0.50768,-0.10128,0.05945],"force_p95":104.0597,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":104.31206,"mean_force":79.85743,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49579,-0.05799,0.03369]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":335.0,"contact_point_centroid":[0.52536,-0.02105,0.03463],"force_p95":38.06072,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":54.17827,"mean_force":8.24354,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49655,0.00651,0.03135]},{"body_a":"peg","body_b":"channel_base_body","contact_count":126.0,"contact_point_centroid":[0.50572,-0.03686,0.0099],"force_p95":15.66335,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.66768,"mean_force":6.3196,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49674,0.00742,0.0315]},{"body_a":"peg","body_b":"channel_base_body","contact_count":467.0,"contact_point_centroid":[0.50566,0.06303,0.00935],"force_p95":0.57957,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.57553,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51203,0.15714,0.21792]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50022,0.19761,0.29544]},{"body_a":"peg","body_b":"channel_base_body","contact_count":990.0,"contact_point_centroid":[0.50585,0.05607,0.00957],"force_p95":1.6705,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.25312,"mean_force":0.84992,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50033,0.09679,0.03269]},{"body_a":"attachment","body_b":"peg","contact_count":338.0,"contact_point_centroid":[0.50365,0.07731,0.04122],"force_p95":1.4277,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.8171,"mean_force":1.10773,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50038,0.08918,0.0321]},{"body_a":"peg","body_b":"channel_base_body","contact_count":556.0,"contact_point_centroid":[0.50602,0.06289,0.00938],"force_p95":0.55144,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55501,"mean_force":0.54657,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51301,0.11528,0.09147]}],"total_contact_groups":9},"final_pose_error":0.02049,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50819,-0.08552,0.03494],"final_tcp_position":[0.4953,-0.06119,0.03338],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"phases":[{"n_steps":495.0,"n_steps_budget":600.0,"object_pos_end":[0.50603,0.063,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14326,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_approach","tcp_end":[0.52445,0.1185,0.14625],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12674,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":556.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.063,0.03381],"object_pos_start":[0.50603,0.063,0.03381],"object_to_goal_dist_end":0.14326,"object_to_goal_dist_start":0.14326,"object_z_max":0.03381,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_descent","tcp_end":[0.50367,0.11259,0.03809],"tcp_start":[0.52445,0.1185,0.14625],"tcp_to_object_dist_end":0.04983,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50683,0.05604,0.03553],"object_pos_start":[0.50593,0.063,0.03381],"object_to_goal_dist_end":0.13629,"object_to_goal_dist_start":0.14326,"object_z_max":0.0356,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","tcp_end":[0.50049,0.08546,0.03192],"tcp_start":[0.50367,0.11259,0.03809],"tcp_to_object_dist_end":0.03031,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":441.0,"n_steps_budget":1000.0,"object_pos_end":[0.50819,-0.08552,0.03494],"object_pos_start":[0.50683,0.05604,0.03553],"object_to_goal_dist_end":0.0111,"object_to_goal_dist_start":0.13629,"object_z_max":0.03724,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"reach_goal","tcp_end":[0.4953,-0.06119,0.03338],"tcp_start":[0.50049,0.08546,0.03192],"tcp_to_object_dist_end":0.02758,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.19792,"average_solve_count":192.0,"average_success_count":192.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.08423,"contact_1.contact_speed":0.01194,"descend_1.descend_speed":0.04128,"push_1.push_speed":0.07095},"optimized_scores":{"best_composite_score":0.31916,"best_fitness_score":0.57916,"best_task_score":0.27544},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":312.0,"contact_point_centroid":[0.50291,-0.00897,0.04822],"force_p95":103.64012,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":112.5756,"mean_force":22.96464,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49704,0.00229,0.0317]},{"body_a":"peg","body_b":"channel_base_body","contact_count":54.0,"contact_point_centroid":[0.50825,-0.10127,0.05989],"force_p95":102.57282,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":103.28155,"mean_force":82.32869,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49586,-0.0579,0.03371]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":316.0,"contact_point_centroid":[0.52532,-0.02781,0.03734],"force_p95":31.26716,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":53.00794,"mean_force":8.77397,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49692,7e-05,0.03168]},{"body_a":"peg","body_b":"channel_base_body","contact_count":124.0,"contact_point_centroid":[0.50698,-0.0391,0.00987],"force_p95":21.70645,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.53016,"mean_force":8.73585,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49711,0.00538,0.03162]},{"body_a":"peg","body_b":"channel_base_body","contact_count":572.0,"contact_point_centroid":[0.50589,0.05664,0.00936],"force_p95":0.60089,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.57429,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5151,0.15433,0.21826]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50015,0.1979,0.29614]},{"body_a":"peg","body_b":"channel_base_body","contact_count":990.0,"contact_point_centroid":[0.50605,0.04971,0.00957],"force_p95":1.67476,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.5333,"mean_force":0.85096,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50093,0.09053,0.03295]},{"body_a":"attachment","body_b":"peg","contact_count":334.0,"contact_point_centroid":[0.50399,0.07098,0.04098],"force_p95":1.40697,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.08379,"mean_force":1.12386,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50094,0.08287,0.03233]},{"body_a":"peg","body_b":"channel_base_body","contact_count":522.0,"contact_point_centroid":[0.50609,0.05657,0.00938],"force_p95":0.55606,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57599,"mean_force":0.54668,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51669,0.10908,0.09146]}],"total_contact_groups":9},"final_pose_error":0.02076,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50816,-0.08482,0.03544],"final_tcp_position":[0.49541,-0.06084,0.03346],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"phases":[{"n_steps":601.0,"n_steps_budget":1000.0,"object_pos_end":[0.50614,0.0566,0.03377],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_approach","tcp_end":[0.53082,0.11235,0.1456],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12736,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":522.0,"n_steps_budget":1000.0,"object_pos_end":[0.50613,0.05663,0.03378],"object_pos_start":[0.50614,0.0566,0.03377],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.13688,"object_z_max":0.03378,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_descent","tcp_end":[0.50438,0.10628,0.03841],"tcp_start":[0.53082,0.11235,0.1456],"tcp_to_object_dist_end":0.04989,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50691,0.04968,0.03553],"object_pos_start":[0.50613,0.05663,0.03378],"object_to_goal_dist_end":0.12994,"object_to_goal_dist_start":0.13691,"object_z_max":0.03555,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","tcp_end":[0.50102,0.07918,0.03213],"tcp_start":[0.50438,0.10628,0.03841],"tcp_to_object_dist_end":0.03027,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":398.0,"n_steps_budget":1000.0,"object_pos_end":[0.50816,-0.08482,0.03544],"object_pos_start":[0.50691,0.04968,0.03553],"object_to_goal_dist_end":0.01052,"object_to_goal_dist_start":0.12994,"object_z_max":0.03683,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"reach_goal","tcp_end":[0.49541,-0.06084,0.03346],"tcp_start":[0.50102,0.07918,0.03213],"tcp_to_object_dist_end":0.02723,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```