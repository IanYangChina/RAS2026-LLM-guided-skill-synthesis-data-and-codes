## Search State

- **Seed**: 0
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.6309 | 0.78 | ✅ accepted |
| 3 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1747 | 0.56 | ❌ rejected |
| 2 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1109 | 0.54 | ❌ rejected |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.6757 | 0.65 | ❌ rejected |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.6280 | 0.69 | ✅ accepted |

**Proposal policy**: task_score is 0.78 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454`
- Frozen object start: [0.5109569349857164, 0.061582937101109625, 0.04]
- Frozen task target: [0.5109569349857164, -0.09841706289889038, 0.04]
- Goal object position: (0.5109569349857164, -0.09841706289889038, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5109569349857164, 0.061582937101109625, 0.04)
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
  frozen_object_start: [0.511, 0.0616, 0.04]
  frozen_task_target: [0.511, -0.0984, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5109569349857164, 0.061582937101109625, 0.04]}
  frozen_targets: {'channel_exit': [0.5109569349857164, -0.09841706289889038, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.781, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5109569349857164, 0.061582937101109625, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5109569349857164, -0.09841706289889038, 0.04) | final destination targets |
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

## Current Skill (Q=0.631) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.04
  - 0.06
  weight: 0.3
- id: insertion_goal
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
    - 0.04
    - 0.06
    tolerance: 0.01
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
  subtask_id: pre_contact
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.025
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 2.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
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
  subtask_id: insertion_goal
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.06], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.025, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.631
- **task_score** (E): 0.781
- **fitness_score**: 0.724  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2075 |
| contact_1 | 0.67 | 1.00 | 0.0705 |
| push_1 | 1.00 | 1.00 | 0.1747 |
| retract_1 | 1.00 | 1.00 | 0.0892 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.125, 0.109) | (0.498, 0.080, 0.040)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.554 | 2.179 |
| contact_1 | contact | 0.67 / force_exceeded | (0.495, 0.125, 0.109)→(0.496, 0.108, 0.041) | (0.500, 0.081, 0.034)→(0.501, 0.079, 0.035) | 0.161→0.159 | 1.00 / 1.667 | 4.806 | 7.241 |
| push_1 | push | 1.00 / step_budget | (0.496, 0.108, 0.041)→(0.493, -0.066, 0.037) | (0.501, 0.079, 0.035)→(0.506, -0.069, 0.032) | 0.159→0.019 | 1.00 / 3.333 | 46.876 | 93.956 |
| retract_1 | retract | 1.00 / step_budget | (0.493, -0.066, 0.037)→(0.490, -0.066, 0.127) | (0.506, -0.069, 0.032)→(0.502, -0.063, 0.027) | 0.019→0.024 | 1.00 / 1.000 | 0.566 | 164.558 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.826
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.826
- phase_score: 0.924
- phase_breakdown.insertion_goal_score: 0.945
- phase_breakdown.pre_contact_score: 0.874

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.885
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.969
- **Median Q (composite search score)**: 0.683
- **K-run variance**: 0.0498
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.405


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `d6915c31707ac435a9367b840736087e39a7a48adfeb36a4f94b6b3ae57cce94`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `19172182883d287409b73cab43749e937e65f1ca1d4501d52b4a913a881aad36`; realized-scene SHA-256: `cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51096,0.06158,0.04]},{"name":"goal","value":[0.51096,-0.09842,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51096,0.06158,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51096,-0.09842,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.3913,"average_solve_count":207.0,"average_success_count":207.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05065,"contact_1.contact_force":5.57018,"push_1.insertion_depth":0.19118,"push_1.push_speed":0.02795},"optimized_scores":{"best_composite_score":0.87465,"best_fitness_score":0.88465,"best_task_score":0.82617},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":434.0,"contact_point_centroid":[0.49815,-0.02691,0.00917],"force_p95":58.87099,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":60.91163,"mean_force":27.91584,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49896,-0.00194,0.04196]},{"body_a":"attachment","body_b":"peg","contact_count":336.0,"contact_point_centroid":[0.49878,-0.0164,0.04345],"force_p95":58.8985,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":60.49615,"mean_force":35.51667,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49908,-0.00791,0.04208]},{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.50074,-0.07036,0.00819],"force_p95":0.67714,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":54.94201,"mean_force":0.87952,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49713,-0.08017,0.08666]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.4963,-0.0909,0.04458],"force_p95":46.26983,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.21259,"mean_force":13.12166,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49975,-0.08123,0.04355]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":15.0,"contact_point_centroid":[0.47496,-0.04551,0.02738],"force_p95":28.5161,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.90194,"mean_force":6.76883,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49966,-0.08128,0.04378]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":69.0,"contact_point_centroid":[0.47491,-0.0288,0.03096],"force_p95":14.82607,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.12747,"mean_force":7.79033,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49876,-0.04221,0.04163]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":10.0,"contact_point_centroid":[0.52501,-0.09495,0.02435],"force_p95":8.95727,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.0543,"mean_force":3.74242,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49704,-0.08007,0.12279]},{"body_a":"peg","body_b":"channel_base_body","contact_count":274.0,"contact_point_centroid":[0.50364,0.06087,0.00938],"force_p95":0.55038,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.92994,"mean_force":0.59074,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50282,0.09877,0.07079]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.503,0.07939,0.05777],"force_p95":6.39238,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.39244,"mean_force":3.34394,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50086,0.09142,0.04672]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":28.0,"contact_point_centroid":[0.52542,0.04325,0.03326],"force_p95":1.08322,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.60158,"mean_force":0.56856,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49745,0.07419,0.04018]},{"body_a":"peg","body_b":"channel_base_body","contact_count":675.0,"contact_point_centroid":[0.50367,0.06158,0.00935],"force_p95":0.58239,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55863,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50275,0.15189,0.19483]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49977,0.19902,0.2984]}],"total_contact_groups":12},"final_pose_error":0.01144,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50649,-0.0706,0.02422],"final_tcp_position":[0.49715,-0.08009,0.13173],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":60.91163,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":698.0,"n_steps_budget":1000.0,"object_pos_end":[0.50374,0.06157,0.03378],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14176,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.54679,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":694.0,"raw_peak_contact_force":2.17216,"subtask_id":"pre_contact","tcp_end":[0.50702,0.10666,0.09806],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07858,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":274.0,"n_steps_budget":600.0,"object_pos_end":[0.50374,0.06123,0.03431],"object_pos_start":[0.50374,0.06157,0.03378],"object_to_goal_dist_end":0.1414,"object_to_goal_dist_start":0.14176,"object_z_max":0.03426,"peak_contact_force":6.59681,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":278.0,"raw_peak_contact_force":6.92994,"tcp_end":[0.50078,0.09085,0.04484],"tcp_start":[0.50702,0.10666,0.09806],"tcp_to_object_dist_end":0.03158,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":486.0,"n_steps_budget":1000.0,"object_pos_end":[0.4935,-0.06982,0.02741],"object_pos_start":[0.50374,0.06123,0.03431],"object_to_goal_dist_end":0.01745,"object_to_goal_dist_start":0.1414,"object_z_max":0.04023,"peak_contact_force":2.22569,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":867.0,"raw_peak_contact_force":60.91163,"subtask_id":"insertion_goal","tcp_end":[0.50011,-0.08062,0.04277],"tcp_start":[0.50078,0.09085,0.04484],"tcp_to_object_dist_end":0.01991,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.50649,-0.0706,0.02422],"object_pos_start":[0.4935,-0.06982,0.02741],"object_to_goal_dist_end":0.01948,"object_to_goal_dist_start":0.01745,"object_z_max":0.02741,"peak_contact_force":0.55322,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":582.0,"raw_peak_contact_force":54.94201,"tcp_end":[0.49715,-0.08009,0.13173],"tcp_start":[0.50011,-0.08062,0.04277],"tcp_to_object_dist_end":0.10833,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `f24211f27d4adabdef509c8ed61621317fdbcaa86fc9ac888f85a717335bb714`; realized-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50095,0.11604,0.04]},{"name":"goal","value":[0.50095,-0.04396,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.11604,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50095,-0.04396,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.31068,"average_solve_count":206.0,"average_success_count":206.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.03624,"contact_1.contact_force":5.66038,"push_1.insertion_depth":0.19964,"push_1.push_speed":0.01656},"optimized_scores":{"best_composite_score":0.68254,"best_fitness_score":0.69254,"best_task_score":0.96891},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":363.0,"contact_point_centroid":[0.49922,0.03684,0.04354],"force_p95":54.26359,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":64.09319,"mean_force":22.81311,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49254,0.04696,0.03836]},{"body_a":"peg","body_b":"channel_base_body","contact_count":530.0,"contact_point_centroid":[0.50636,-0.05535,0.0096],"force_p95":0.97161,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.38246,"mean_force":0.67287,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48975,-0.03558,0.08389]},{"body_a":"attachment","body_b":"peg","contact_count":54.0,"contact_point_centroid":[0.49732,-0.04527,0.05127],"force_p95":7.8013,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.03783,"mean_force":2.41589,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49038,-0.03578,0.05237]},{"body_a":"peg","body_b":"channel_base_body","contact_count":280.0,"contact_point_centroid":[0.50662,0.00439,0.00985],"force_p95":38.79383,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.857,"mean_force":17.0509,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49267,0.04303,0.03858]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":413.0,"contact_point_centroid":[0.5255,0.0201,0.03515],"force_p95":41.23824,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.67724,"mean_force":14.22466,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4925,0.04477,0.03831]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":120.0,"contact_point_centroid":[0.52524,-0.05593,0.04588],"force_p95":7.11951,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.23517,"mean_force":0.9566,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49027,-0.03576,0.05671]},{"body_a":"peg","body_b":"channel_base_body","contact_count":252.0,"contact_point_centroid":[0.50138,0.11432,0.00944],"force_p95":0.62895,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.38294,"mean_force":0.63337,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49579,0.15099,0.06315]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.49913,0.1334,0.05657],"force_p95":6.26537,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.9942,"mean_force":3.26868,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49613,0.14535,0.04535]},{"body_a":"peg","body_b":"channel_base_body","contact_count":646.0,"contact_point_centroid":[0.50093,0.11602,0.00938],"force_p95":0.62307,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55657,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49797,0.17827,0.18996]}],"total_contact_groups":9},"final_pose_error":0.01114,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50658,-0.04933,0.03391],"final_tcp_position":[0.48984,-0.03555,0.1282],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":64.09319,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":662.0,"n_steps_budget":1000.0,"object_pos_end":[0.50092,0.11613,0.03389],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19622,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.5699,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":646.0,"raw_peak_contact_force":1.92055,"subtask_id":"pre_contact","tcp_end":[0.49759,0.15778,0.08548],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06639,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":252.0,"n_steps_budget":600.0,"object_pos_end":[0.50097,0.1152,0.03492],"object_pos_start":[0.50092,0.11613,0.03389],"object_to_goal_dist_end":0.19527,"object_to_goal_dist_start":0.19622,"object_z_max":0.03487,"peak_contact_force":7.38294,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":260.0,"raw_peak_contact_force":7.38294,"tcp_end":[0.49629,0.14457,0.04285],"tcp_start":[0.49759,0.15778,0.08548],"tcp_to_object_dist_end":0.03078,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":515.0,"n_steps_budget":1000.0,"object_pos_end":[0.50887,-0.06129,0.03983],"object_pos_start":[0.50097,0.1152,0.03492],"object_to_goal_dist_end":0.02071,"object_to_goal_dist_start":0.19527,"object_z_max":0.03983,"peak_contact_force":63.57625,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1056.0,"raw_peak_contact_force":64.09319,"subtask_id":"insertion_goal","tcp_end":[0.49277,-0.03586,0.03895],"tcp_start":[0.49629,0.14457,0.04285],"tcp_to_object_dist_end":0.03012,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":544.0,"n_steps_budget":630.0,"object_pos_end":[0.50658,-0.04933,0.03391],"object_pos_start":[0.50887,-0.06129,0.03983],"object_to_goal_dist_end":0.03195,"object_to_goal_dist_start":0.02071,"object_z_max":0.04064,"peak_contact_force":0.5425,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":704.0,"raw_peak_contact_force":50.38246,"tcp_end":[0.48984,-0.03555,0.1282],"tcp_start":[0.49277,-0.03586,0.03895],"tcp_to_object_dist_end":0.09675,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `d098a7862ff18c9bbe982af3446a89a0fa6bcfa8790d7d955f65b2375d67a881`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47929,"average_solve_count":169.0,"average_success_count":169.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09672,"contact_1.contact_force":8.44248,"push_1.insertion_depth":0.19094,"push_1.push_speed":0.04654},"optimized_scores":{"best_composite_score":0.33563,"best_fitness_score":0.59563,"best_task_score":0.54839},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":146.0,"contact_point_centroid":[0.47495,-0.081,0.04515],"force_p95":352.78706,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":388.34973,"mean_force":204.59938,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48676,-0.08097,0.04333]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":495.0,"contact_point_centroid":[0.47499,-0.0163,0.03394],"force_p95":133.13682,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":156.86301,"mean_force":93.02849,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48684,-0.01629,0.03214]},{"body_a":"attachment","body_b":"peg","contact_count":799.0,"contact_point_centroid":[0.49677,-0.0134,0.03347],"force_p95":129.22053,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":138.51753,"mean_force":76.48537,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48688,-0.00961,0.03212]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":795.0,"contact_point_centroid":[0.52736,-0.02058,0.03183],"force_p95":119.61277,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":132.16538,"mean_force":70.31519,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48686,-0.01061,0.03211]},{"body_a":"attachment","body_b":"peg","contact_count":90.0,"contact_point_centroid":[0.49833,-0.08138,0.03524],"force_p95":91.89835,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":106.69384,"mean_force":47.37599,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48675,-0.08139,0.03673]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":111.0,"contact_point_centroid":[0.52799,-0.08319,0.02784],"force_p95":96.59813,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":106.16308,"mean_force":43.4074,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48676,-0.0812,0.03823]},{"body_a":"peg","body_b":"channel_base_body","contact_count":707.0,"contact_point_centroid":[0.51072,-0.02196,0.00958],"force_p95":77.97363,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":86.79936,"mean_force":41.89319,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48694,-0.00177,0.03227]},{"body_a":"peg","body_b":"link7","contact_count":515.0,"contact_point_centroid":[0.51645,-0.01635,0.06894],"force_p95":52.28098,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":61.20187,"mean_force":28.52863,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48686,-0.00362,0.03247]},{"body_a":"peg","body_b":"channel_base_body","contact_count":510.0,"contact_point_centroid":[0.49782,-0.07048,0.00842],"force_p95":22.09418,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.00585,"mean_force":3.10381,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48478,-0.08141,0.0771]},{"body_a":"peg","body_b":"channel_base_body","contact_count":68.0,"contact_point_centroid":[0.51207,-0.10011,0.02937],"force_p95":35.14308,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.26331,"mean_force":12.37021,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48683,-0.07697,0.03089]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":41.0,"contact_point_centroid":[0.47494,-0.06902,0.02462],"force_p95":9.87011,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.42581,"mean_force":3.86916,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48398,-0.08165,0.07668]},{"body_a":"peg","body_b":"channel_base_body","contact_count":628.0,"contact_point_centroid":[0.49557,0.06106,0.00943],"force_p95":1.16182,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.41115,"mean_force":0.68503,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48374,0.09963,0.08825]},{"body_a":"attachment","body_b":"peg","contact_count":42.0,"contact_point_centroid":[0.49287,0.07975,0.05637],"force_p95":6.51356,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.09838,"mean_force":2.33781,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48919,0.09156,0.04614]},{"body_a":"peg","body_b":"channel_base_body","contact_count":5.0,"contact_point_centroid":[0.50859,-0.10012,0.03373],"force_p95":2.53735,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.58337,"mean_force":1.26035,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48683,-0.08264,0.03066]},{"body_a":"peg","body_b":"channel_base_body","contact_count":535.0,"contact_point_centroid":[0.49545,0.06378,0.00937],"force_p95":0.5843,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56146,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48865,0.15347,0.21789]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49929,0.19829,0.29715]}],"total_contact_groups":16},"final_pose_error":0.01121,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49442,-0.07025,0.02413],"final_tcp_position":[0.48384,-0.08187,0.11982],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":388.34973,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":562.0,"n_steps_budget":1000.0,"object_pos_end":[0.49529,0.06395,0.03394],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14416,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54662,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":563.0,"raw_peak_contact_force":2.44546,"subtask_id":"pre_contact","tcp_end":[0.47946,0.11028,0.1442],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12064,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":635.0,"n_steps_budget":720.0,"object_pos_end":[0.49748,0.06035,0.03504],"object_pos_start":[0.49529,0.06395,0.03394],"object_to_goal_dist_end":0.14046,"object_to_goal_dist_start":0.14416,"object_z_max":0.03581,"peak_contact_force":0.43964,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":670.0,"raw_peak_contact_force":7.41115,"tcp_end":[0.49054,0.08957,0.0358],"tcp_start":[0.47946,0.11028,0.1442],"tcp_to_object_dist_end":0.03005,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":859.0,"n_steps_budget":1000.0,"object_pos_end":[0.51474,-0.07518,0.02808],"object_pos_start":[0.49748,0.06035,0.03504],"object_to_goal_dist_end":0.01956,"object_to_goal_dist_start":0.14046,"object_z_max":0.03967,"peak_contact_force":74.82619,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3379.0,"raw_peak_contact_force":156.86301,"subtask_id":"insertion_goal","tcp_end":[0.48679,-0.08246,0.03062],"tcp_start":[0.49054,0.08957,0.0358],"tcp_to_object_dist_end":0.029,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.49442,-0.07025,0.02413],"object_pos_start":[0.51474,-0.07518,0.02808],"object_to_goal_dist_end":0.01944,"object_to_goal_dist_start":0.01956,"object_z_max":0.0288,"peak_contact_force":0.60161,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":903.0,"raw_peak_contact_force":388.34973,"tcp_end":[0.48384,-0.08187,0.11982],"tcp_start":[0.48679,-0.08246,0.03062],"tcp_to_object_dist_end":0.09697,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```