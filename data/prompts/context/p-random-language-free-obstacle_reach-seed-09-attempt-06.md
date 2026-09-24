## Search State

- **Seed**: 9
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → align → descend | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.5662 | 0.95 | ✅ accepted |
| 5 | approach → align → descend | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.5310 | 0.91 | ❌ rejected |
| 4 | approach → align → descend | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.5662 | 0.95 | ✅ accepted |
| 3 | approach → align → descend | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5327 | 0.86 | ✅ accepted |
| 2 | approach → align → descend | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5276 | 0.86 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.95). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

- Task name: obstacle_reach
- Frozen realised-scene SHA-256: `fda113aaf8e8c099f2c28b9d9dc98e35a2e52600fa9b3eec61a8dea75fa26f9a`
- Frozen task target: [0.7370249203970084, -0.021318279091244466, 0.15]
- Goal object position: (0.7370249203970084, -0.021318279091244466, 0.15)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.5
- Force limit: 5.0 N
- Obstacle body: obstacle_block (contact = collision penalty)
- Robot initial TCP position: (0.35, 0.0, 0.32)
- Primary evaluation target: **TCP distance to goal position (Gaussian proximity kernel)**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.35, 0, 0.32]
objects:
  - name: obstacle_block
    role: obstacle
    dynamics: static
    geometry: box
    dimensions_m: [0.08, 0.3, 0.3]
  - name: goal_marker
    role: target_marker
    dynamics: static
    geometry: point
task_landmarks:
  frozen_task_target: [0.737, -0.0213, 0.15]
  frozen_obstacle_position: [0.5, 0, 0.15]
  frozen_targets: {'task_goal': [0.7370249203970084, -0.021318279091244466, 0.15]}
  frozen_obstacles: {'obstacle_block': [0.5, 0.0, 0.15]}
  goal_tolerance_m: 0.02
  force_limit_n: 5
  obstacle_height_m: 0.3
  force_scale_n: 5
  realized_scene_sha256: fda113aaf8e8c099f2c28b9d9dc98e35a2e52600fa9b3eec61a8dea75fa26f9a

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.946, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position | approach/contact targets near object |
| `goal` | offset from task goal position (0.7370249203970084, -0.021318279091244466, 0.15) | final destination targets |
| `fixture` | offset from fixture pose (0.5, 0.0, 0.15) | approach/contact targets near fixture |

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

## Current Skill (Q=0.566) — your mutation base

```yaml
skill: obstacle_reach
dsl_version: 2
subtasks:
- id: pre_approach
  offset:
  - 0.0
  - 0.15
  - 0.15
  weight: 0.3
- id: final_goal
  weight: 0.7
phases:
- id: approach_clearance
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.15
    - 0.15
    tolerance: 0.05
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.4
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    approach_y:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.y
        mode: replace
    approach_z:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: collision_avoid
    when: during_phase
    predicate: force_below
    threshold: 2.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.05
    - 0.0
  subtask_id: pre_approach
- id: align_to_goal
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    align_z:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: final_goal
- id: descend_to_goal
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: final_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_clearance** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.15, 0.15], tolerance=0.05
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - approach_y: status=consumed; consumers=target.offset.y (replace)
    - approach_z: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=collision_avoid, when=during_phase, predicate=force_below, on_failure=retry, threshold=2.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.05, 0.0]
- **align_to_goal** (`align`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
    - align_z: status=consumed; consumers=target.offset.z (replace)
- **descend_to_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.566
- **task_score** (E): 0.946
- **fitness_score**: 0.946  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_clearance | 0.33 | 0.00 | 0.3323 |
| align_to_goal | 1.00 | 0.00 | 0.2030 |
| descend_to_goal | 1.00 | 0.00 | 0.0492 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_clearance | approach | 0.33 / step_budget | (0.350, -0.000, 0.321)→(0.655, 0.130, 0.341) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.731→0.731 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_to_goal | align | 1.00 / step_budget | (0.655, 0.130, 0.341)→(0.709, -0.008, 0.204) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.731→0.731 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_to_goal | descend | 1.00 / step_budget | (0.709, -0.008, 0.204)→(0.710, -0.013, 0.155) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.731→0.731 | 0.00 / 0.000 | 0.000 | 0.000 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- obstacle_clearance: 0.351
- path_efficiency: 0.614
- arc_smoothness: 0.992
- collision_factor: 1.000  (exp(−peak_force / force_scale))
- peak_obstacle_force: 0.000 N
- collision_location: obstacle_block  (or None if no contact)
- final_tcp_distance: 0.005
- min_tcp_distance: 0.005
- tcp_proximity_score: 0.968
- goal_reached_rate: 1.000
- peak_obstacle_counterbody: None
- peak_obstacle_countergeom: None
- peak_obstacle_obstacle_body: None
- peak_obstacle_obstacle_geom: None

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.968
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.968
- **Median Q (composite search score)**: 0.588
- **K-run variance**: 0.0010
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.196


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `4a44882555f0d0b14e6aa599db443a998da24652eb9b9e2830cc337dec76aa35`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `47104ba1d83b6713840746a9744b8461d7698be90a7b9bbdb4a5ee2c9b597658`; realized-scene SHA-256: `fda113aaf8e8c099f2c28b9d9dc98e35a2e52600fa9b3eec61a8dea75fa26f9a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.73702,-0.02132,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.73702,-0.02132,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":2.0,"average_failure_rate":0.02128,"average_mean_iterations":8.2766,"average_solve_count":94.0,"average_success_count":92.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_goal.align_speed":0.11841,"align_to_goal.align_z":0.05857,"approach_clearance.approach_speed":0.23041,"approach_clearance.approach_tolerance":0.06412,"approach_clearance.approach_y":0.17622,"approach_clearance.approach_z":0.19504,"descend_to_goal.descend_speed":0.105},"optimized_scores":{"best_composite_score":0.58806,"best_fitness_score":0.96806,"best_task_score":0.96806},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.00487,"key_states":{"actual_goal_position":[0.73702,-0.02132,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.73296,-0.01969,0.15214],"realised_goal_position":[0.73702,-0.02132,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":308.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75244,"object_to_goal_dist_start":0.75244,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_clearance","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_approach","tcp_end":[0.67144,0.12656,0.3368],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.76176,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":712.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75244,"object_to_goal_dist_start":0.75244,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"align_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"final_goal","tcp_end":[0.73153,-0.01353,0.20595],"tcp_start":[0.67144,0.12656,0.3368],"tcp_to_object_dist_end":0.76009,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":192.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75244,"object_to_goal_dist_start":0.75244,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"final_goal","tcp_end":[0.73296,-0.01969,0.15214],"tcp_start":[0.73153,-0.01353,0.20595],"tcp_to_object_dist_end":0.74885,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `dd76534a039a46a09f9e3c15723c51c6f1027acc2aa2ab4b06e8dae86dbdcd96`; realized-scene SHA-256: `61ec300895503e484321052c14122005b6d825b54245a4a918a581ea2f04a59f`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.7456,-0.02923,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.7456,-0.02923,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":11.0,"average_failure_rate":0.11957,"average_mean_iterations":27.75,"average_solve_count":92.0,"average_success_count":81.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_goal.align_speed":0.11414,"align_to_goal.align_z":0.02052,"approach_clearance.approach_speed":0.31553,"approach_clearance.approach_tolerance":0.04407,"approach_clearance.approach_y":0.17225,"approach_clearance.approach_z":0.20935,"descend_to_goal.descend_speed":0.07859},"optimized_scores":{"best_composite_score":0.52236,"best_fitness_score":0.90236,"best_task_score":0.90236},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.01541,"key_states":{"actual_goal_position":[0.7456,-0.02923,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.73875,-0.02141,0.16138],"realised_goal_position":[0.7456,-0.02923,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":293.0,"n_steps_budget":840.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.7611,"object_to_goal_dist_start":0.7611,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_clearance","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_approach","tcp_end":[0.67179,0.11441,0.348],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.76518,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":706.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.7611,"object_to_goal_dist_start":0.7611,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"align_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"final_goal","tcp_end":[0.73782,-0.01803,0.17407],"tcp_start":[0.67179,0.11441,0.348],"tcp_to_object_dist_end":0.75829,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":53.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.7611,"object_to_goal_dist_start":0.7611,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"final_goal","tcp_end":[0.73875,-0.02141,0.16138],"tcp_start":[0.73782,-0.01803,0.17407],"tcp_to_object_dist_end":0.75648,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b9c2919c979234936a5d994fa5db826639b75dec9196808e9cc353d4e638017c`; realized-scene SHA-256: `8ce05051d0a4672b6b8279618e8bd34ed9ec87b7d3e4b0ff82cc182ecfb81133`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.66286,-7e-05,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.66286,-7e-05,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.36364,"average_solve_count":99.0,"average_success_count":99.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_goal.align_speed":0.12383,"align_to_goal.align_z":0.08499,"approach_clearance.approach_speed":0.15621,"approach_clearance.approach_tolerance":0.06034,"approach_clearance.approach_y":0.17337,"approach_clearance.approach_z":0.19588,"descend_to_goal.descend_speed":0.12959},"optimized_scores":{"best_composite_score":0.58806,"best_fitness_score":0.96806,"best_task_score":0.96806},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.00487,"key_states":{"actual_goal_position":[0.66286,-7e-05,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.65891,0.00089,0.15269],"realised_goal_position":[0.66286,-7e-05,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":291.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.67962,"object_to_goal_dist_start":0.67962,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_clearance","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_approach","tcp_end":[0.62084,0.14815,0.33921],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.72281,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":653.0,"n_steps_budget":960.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.67962,"object_to_goal_dist_start":0.67962,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"align_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"final_goal","tcp_end":[0.65808,0.00828,0.23273],"tcp_start":[0.62084,0.14815,0.33921],"tcp_to_object_dist_end":0.69807,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":298.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.67962,"object_to_goal_dist_start":0.67962,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"final_goal","tcp_end":[0.65891,0.00089,0.15269],"tcp_start":[0.65808,0.00828,0.23273],"tcp_to_object_dist_end":0.67637,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```